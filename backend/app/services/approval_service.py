from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.workflow import ApprovalWorkflow
from app.models.enums import InvoiceStatus
from app.schemas.approval import PendingInvoiceResponse, ApprovalHistoryResponse
from app.services.invoice_service import create_audit_log

def submit_for_approval(db: Session, invoice_id: int, actor_id: int):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
        
    if invoice.status != InvoiceStatus.VALIDATION_PASSED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only VALIDATION_PASSED invoices can be submitted for approval.")
        
    existing_workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.invoice_id == invoice_id).first()
    if existing_workflow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice has already been submitted for approval.")
        
    workflow = ApprovalWorkflow(
        invoice_id=invoice_id,
        status=InvoiceStatus.PENDING_APPROVAL
    )
    db.add(workflow)
    
    invoice.status = InvoiceStatus.PENDING_APPROVAL
    
    create_audit_log(db, invoice_id, actor_id, "Invoice Submitted For Approval", "Workflow initiated.")
    db.commit()
    return {"message": "Invoice submitted for approval successfully."}

def approve_invoice(db: Session, invoice_id: int, comments: str, actor_id: int):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
        
    if invoice.status != InvoiceStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice is not PENDING_APPROVAL.")
        
    workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.invoice_id == invoice_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval workflow not found for this invoice.")
        
    workflow.approver_id = actor_id
    workflow.comments = comments
    workflow.actioned_at = func.now()
    workflow.status = InvoiceStatus.APPROVED
    
    invoice.status = InvoiceStatus.APPROVED
    
    create_audit_log(db, invoice_id, actor_id, "Invoice Approved", comments)
    db.commit()
    return {"message": "Invoice approved successfully."}

def reject_invoice(db: Session, invoice_id: int, comments: str, actor_id: int):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
        
    if invoice.status != InvoiceStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice is not PENDING_APPROVAL.")
        
    workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.invoice_id == invoice_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval workflow not found for this invoice.")
        
    workflow.approver_id = actor_id
    workflow.comments = comments
    workflow.actioned_at = func.now()
    workflow.status = InvoiceStatus.REJECTED
    
    invoice.status = InvoiceStatus.REJECTED
    
    create_audit_log(db, invoice_id, actor_id, "Invoice Rejected", comments)
    db.commit()
    return {"message": "Invoice rejected successfully."}

def get_pending_invoices(db: Session) -> List[PendingInvoiceResponse]:
    invoices = (
        db.query(Invoice)
        .join(Vendor, Invoice.vendor_id == Vendor.id)
        .filter(Invoice.status == InvoiceStatus.PENDING_APPROVAL)
        .all()
    )
    
    results = []
    for inv in invoices:
        results.append(PendingInvoiceResponse(
            invoice_id=inv.id,
            invoice_number=inv.invoice_number,
            vendor_name=inv.vendor.name if inv.vendor else "Unknown",
            total_amount=inv.total_amount or 0.0,
            status=inv.status.value
        ))
    return results

def get_approval_history(db: Session, invoice_id: int) -> ApprovalHistoryResponse:
    workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.invoice_id == invoice_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval workflow not found for this invoice.")
        
    approver_name = None
    if workflow.approver:
        approver_name = workflow.approver.email
        
    return ApprovalHistoryResponse(
        invoice_id=workflow.invoice_id,
        submitted_at=workflow.created_at,
        approved_by=approver_name,
        status=workflow.status.value,
        comments=workflow.comments,
        actioned_at=workflow.actioned_at
    )
