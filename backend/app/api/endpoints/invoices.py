import os
import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.invoice import InvoiceProcessingSummary
from app.schemas.po_match import POMatchRequest, POMatchResponse
from app.schemas.approval import ApprovalActionRequest, PendingInvoiceResponse, ApprovalHistoryResponse
from app.services.invoice_service import process_invoice_upload
from app.services.po_matching_service import calculate_po_match, execute_po_match
from app.services.approval_service import (
    submit_for_approval,
    approve_invoice,
    reject_invoice,
    get_pending_invoices,
    get_approval_history
)

router = APIRouter()

UPLOAD_DIR = "uploads/invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload", response_model=InvoiceProcessingSummary)
def upload_invoice(
    vendor_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an invoice for processing.
    """
    # File type validation
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # File size validation
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )

    # Generate unique filename and save
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
        
    # Trigger pipeline
    try:
        summary = process_invoice_upload(db, vendor_id, file_path, current_user.id)
        return summary
    except Exception as e:
        # If pipeline throws unexpectedly
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}"
        )

@router.get("/pending-approval", response_model=list[PendingInvoiceResponse])
def get_pending_invoices_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of all invoices currently awaiting approval.
    """
    return get_pending_invoices(db)

@router.post("/{invoice_id}/po-match", response_model=POMatchResponse)
def match_purchase_order(
    invoice_id: int,
    request: POMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes the Purchase Order matching process for a given invoice.
    """
    return execute_po_match(db, invoice_id, request.po_id, current_user.id)

@router.get("/{invoice_id}/po-match", response_model=POMatchResponse)
def get_purchase_order_match(
    invoice_id: int,
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dynamically recalculates and returns the PO match result.
    """
    return calculate_po_match(db, invoice_id, po_id)

@router.post("/{invoice_id}/submit")
def submit_invoice_for_approval(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FINANCE]))
):
    """
    Submits a validated invoice for approval. Limited to ADMIN and FINANCE.
    """
    return submit_for_approval(db, invoice_id, current_user.id)

@router.post("/{invoice_id}/approve")
def approve_invoice_endpoint(
    invoice_id: int,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.APPROVER]))
):
    """
    Approves a pending invoice. Limited to APPROVER.
    """
    return approve_invoice(db, invoice_id, request.comments, current_user.id)

@router.post("/{invoice_id}/reject")
def reject_invoice_endpoint(
    invoice_id: int,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.APPROVER]))
):
    """
    Rejects a pending invoice. Limited to APPROVER.
    """
    return reject_invoice(db, invoice_id, request.comments, current_user.id)

@router.get("/{invoice_id}/approval-history", response_model=ApprovalHistoryResponse)
def get_approval_history_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the approval history and status for a given invoice.
    """
    return get_approval_history(db, invoice_id)
