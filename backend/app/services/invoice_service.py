import os
import uuid
import datetime
from sqlalchemy.orm import Session
from app.models.invoice import Invoice, InvoiceLineItem
from app.models.audit import AuditLog
from app.models.enums import InvoiceStatus
from app.schemas.invoice import InvoiceProcessingSummary, InvoiceOCRResult
from app.services.ocr_service import extract_invoice_data
from app.services.validation_service import validate_invoice_data, check_duplicate_invoice

def parse_date(date_str: str):
    if not date_str:
        return None
    try:
        # Assuming Gemini returns YYYY-MM-DD based on prompt
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def create_audit_log(db: Session, invoice_id: int, actor_id: int, action: str, details: str):
    log = AuditLog(
        invoice_id=invoice_id,
        actor_id=actor_id,
        action=action,
        details=details
    )
    db.add(log)
    db.commit()

def process_invoice_upload(db: Session, vendor_id: int, file_path: str, current_user_id: int) -> InvoiceProcessingSummary:
    """
    Orchestrates the invoice upload pipeline.
    """
    # 1. Create Invoice record immediately
    # Schema requires invoice_number, use a placeholder until OCR completes
    temp_invoice_number = f"PENDING_{uuid.uuid4().hex[:8].upper()}"
    
    invoice = Invoice(
        vendor_id=vendor_id,
        invoice_number=temp_invoice_number,
        file_path=file_path,
        status=InvoiceStatus.UPLOADED
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    create_audit_log(db, invoice.id, current_user_id, "Invoice Uploaded", f"File: {os.path.basename(file_path)}")

    # 2. OCR Runs
    ocr_dict, confidence = extract_invoice_data(file_path)
    
    if not ocr_dict:
        # OCR Failure
        invoice.status = InvoiceStatus.VALIDATION_FAILED
        db.commit()
        create_audit_log(db, invoice.id, current_user_id, "OCR Failure", "Failed to extract data from Gemini API")
        return InvoiceProcessingSummary(
            invoice_id=invoice.id,
            status=invoice.status,
            validation_errors=["OCR failed to extract data"]
        )
    
    ocr_result = InvoiceOCRResult(**ocr_dict)
    
    # Update OCR details and status to EXTRACTED
    invoice.status = InvoiceStatus.EXTRACTED
    invoice.ocr_confidence = confidence if confidence is not None else 0.95
    
    # Try to parse date
    if ocr_result.invoice_date:
        invoice.invoice_date = parse_date(ocr_result.invoice_date)
            
    # Update amounts
    invoice.subtotal = ocr_result.subtotal
    invoice.gst_amount = ocr_result.gst_amount
    invoice.total_amount = ocr_result.total_amount
    
    # Temporarily update invoice_number if found, but handle duplicate constraint
    if ocr_result.invoice_number:
        # Check duplicate before assigning
        if check_duplicate_invoice(db, vendor_id, ocr_result.invoice_number, invoice.id):
            # Let validation catch it, keep temp or assign and let flush fail?
            # It's better to keep temp and let validation report it, so it doesn't crash on commit
            pass
        else:
            invoice.invoice_number = ocr_result.invoice_number

    db.commit()
    create_audit_log(db, invoice.id, current_user_id, "OCR Completed", "Successfully extracted invoice data")

    # 3. Validation Runs
    errors = validate_invoice_data(db, vendor_id, ocr_result)
    
    # Additional Duplicate Check (since validation service doesn't have the current_invoice_id context easily)
    if ocr_result.invoice_number and check_duplicate_invoice(db, vendor_id, ocr_result.invoice_number, invoice.id):
        errors.append(f"Duplicate invoice number '{ocr_result.invoice_number}' for this vendor")
        
    if errors:
        invoice.status = InvoiceStatus.VALIDATION_FAILED
        db.commit()
        create_audit_log(db, invoice.id, current_user_id, "Validation Failed", f"Errors: {', '.join(errors)}")
    else:
        invoice.status = InvoiceStatus.VALIDATION_PASSED
        
        # Save line items only if validation passed (or you can save them anyway, depending on preference. Let's save them)
        if ocr_result.line_items:
            for item in ocr_result.line_items:
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total
                )
                db.add(line_item)
                
        db.commit()
        create_audit_log(db, invoice.id, current_user_id, "Validation Passed", "Invoice data validated successfully")

    return InvoiceProcessingSummary(
        invoice_id=invoice.id,
        status=invoice.status,
        ocr_data=ocr_result,
        validation_errors=errors
    )

def get_invoices(db: Session, search: str = None, status: InvoiceStatus = None, page: int = 1, size: int = 20):
    query = db.query(Invoice)
    
    if status:
        query = query.filter(Invoice.status == status)
        
    if search:
        query = query.filter(Invoice.invoice_number.ilike(f"%{search}%"))
        
    total = query.count()
    invoices = query.order_by(Invoice.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "data": invoices,
        "total": total,
        "page": page,
        "size": size
    }

def get_invoice_detail(db: Session, invoice_id: int):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return None
        
    vendor_name = invoice.vendor.name if invoice.vendor else "Unknown Vendor"
    
    # Audit logs
    audit_logs = [
        {
            "id": log.id,
            "action": log.action,
            "details": log.details,
            "actor_email": log.actor.email if log.actor else "System",
            "timestamp": log.created_at
        }
        for log in invoice.audit_logs
    ]
    
    # Approval history (workflow)
    approval_history = []
    if invoice.workflow:
        approval_history.append({
            "status": invoice.workflow.status.value,
            "approver_email": invoice.workflow.approver.email if invoice.workflow.approver else None,
            "comments": invoice.workflow.comments,
            "actioned_at": invoice.workflow.actioned_at
        })
        
    # Line items
    line_items = [
        {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": item.line_total
        }
        for item in invoice.line_items
    ]
    
    return {
        "invoice": invoice,
        "vendor_name": vendor_name,
        "line_items": line_items,
        "approval_history": approval_history,
        "audit_logs": sorted(audit_logs, key=lambda x: x["timestamp"], reverse=True)[:10] # Recent 10
    }
