import json
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.models.enums import InvoiceStatus, VendorStatus
from app.schemas.po_match import POMatchResponse
from app.services.invoice_service import create_audit_log

TOLERANCE = 0.01

def calculate_po_match(db: Session, invoice_id: int, po_id: int) -> POMatchResponse:
    """
    Dynamically recalculates the PO Match without persisting to AuditLog.
    """
    details = []
    
    # 1. Load Invoice
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=0, invoice_amount=0, details=["Invoice not found."])
        
    if invoice.status != InvoiceStatus.VALIDATION_PASSED:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=0, invoice_amount=invoice.total_amount or 0, details=["Invoice status must be VALIDATION_PASSED."])

    # 2. Load PurchaseOrder
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=0, invoice_amount=invoice.total_amount or 0, details=["PurchaseOrder not found."])
        
    # 3. Load Vendor
    vendor = db.query(Vendor).filter(Vendor.id == po.vendor_id).first()
    if not vendor:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=po.amount or 0, invoice_amount=invoice.total_amount or 0, details=["Vendor not found."])
        
    if vendor.status != VendorStatus.ACTIVE:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=po.amount or 0, invoice_amount=invoice.total_amount or 0, details=["Vendor is not ACTIVE."])
        
    if invoice.vendor_id != po.vendor_id:
        return POMatchResponse(match_type="UNKNOWN", result="MISMATCH", vendor_match=False, po_amount=po.amount or 0, invoice_amount=invoice.total_amount or 0, details=["Invoice vendor does not match PurchaseOrder vendor."])

    # 4. Load GRNs
    grns = po.grns
    
    po_amt = po.amount or 0.0
    inv_amt = invoice.total_amount or 0.0
    
    if not grns:
        # Two-Way Match
        match_type = "TWO_WAY"
        if abs(po_amt - inv_amt) <= TOLERANCE:
            result = "MATCHED"
            details.append("PO amount matches Invoice amount.")
        else:
            result = "MISMATCH"
            details.append("PO amount differs from Invoice amount.")
            
        return POMatchResponse(
            match_type=match_type,
            result=result,
            vendor_match=True,
            po_amount=po_amt,
            grn_amount=None,
            invoice_amount=inv_amt,
            details=details
        )
    else:
        # Three-Way Match
        match_type = "THREE_WAY"
        grn_amt = sum(grn.received_amount or 0.0 for grn in grns)
        
        po_eq_inv = abs(po_amt - inv_amt) <= TOLERANCE
        po_eq_grn = abs(po_amt - grn_amt) <= TOLERANCE
        grn_eq_inv = abs(grn_amt - inv_amt) <= TOLERANCE
        
        if po_eq_inv and po_eq_grn and grn_eq_inv:
            result = "MATCHED"
            details.append("PO, GRN, and Invoice amounts all match.")
        elif po_eq_inv or po_eq_grn or grn_eq_inv:
            result = "PARTIAL_MATCH"
            if po_eq_inv:
                details.append("PO amount matches Invoice, but GRN differs.")
            elif po_eq_grn:
                details.append("PO amount matches GRN, but Invoice differs.")
            elif grn_eq_inv:
                details.append("GRN amount matches Invoice, but PO differs.")
        else:
            result = "MISMATCH"
            details.append("No amounts match (PO, GRN, Invoice all differ).")
            
        return POMatchResponse(
            match_type=match_type,
            result=result,
            vendor_match=True,
            po_amount=po_amt,
            grn_amount=grn_amt,
            invoice_amount=inv_amt,
            details=details
        )

def execute_po_match(db: Session, invoice_id: int, po_id: int, actor_id: int) -> POMatchResponse:
    """
    Executes the PO Match, creates AuditLog entries, and returns the response.
    """
    create_audit_log(db, invoice_id, actor_id, "PO Match Executed", f"Started matching against PO ID: {po_id}")
    
    response = calculate_po_match(db, invoice_id, po_id)
    
    # Audit log the specific result
    if response.result == "MATCHED":
        action = "PO Match Passed"
    elif response.result == "PARTIAL_MATCH":
        action = "PO Match Partial"
    else:
        action = "PO Match Failed"
        
    audit_details = json.dumps(response.model_dump())
    create_audit_log(db, invoice_id, actor_id, action, audit_details)
    
    return response
