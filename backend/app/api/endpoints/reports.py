from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.report import (
    InvoiceStatusReportItem,
    VendorReportItem,
    PaginatedAuditReport,
    PaginatedApprovalReport
)
from app.services.report_service import (
    get_invoice_status_report,
    get_vendor_report,
    get_audit_report,
    get_approval_report
)

router = APIRouter()

@router.get("/invoice-status", response_model=List[InvoiceStatusReportItem])
def invoice_status_report_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Groups invoices by status and returns counts.
    """
    return get_invoice_status_report(db)

@router.get("/vendor-report", response_model=List[VendorReportItem])
def vendor_report_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns vendor name alongside total, approved, and rejected invoice counts.
    """
    return get_vendor_report(db)

@router.get("/audit-report", response_model=PaginatedAuditReport)
def audit_report_endpoint(
    start_date: Optional[datetime] = Query(None, description="Filter logs starting from this date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Filter logs up to this date (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns paginated AuditLog entries with optional date filtering.
    """
    return get_audit_report(db, start_date=start_date, end_date=end_date, page=page, size=size)

@router.get("/approval-report", response_model=PaginatedApprovalReport)
def approval_report_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns paginated data for approved and rejected invoices, including approver details and comments.
    """
    return get_approval_report(db, page=page, size=size)
