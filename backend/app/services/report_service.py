from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.audit import AuditLog
from app.models.workflow import ApprovalWorkflow
from app.models.enums import InvoiceStatus
from app.schemas.report import (
    InvoiceStatusReportItem,
    VendorReportItem,
    AuditReportItem,
    PaginatedAuditReport,
    ApprovalReportItem,
    PaginatedApprovalReport
)

def get_invoice_status_report(db: Session) -> List[InvoiceStatusReportItem]:
    counts = db.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all()
    return [InvoiceStatusReportItem(status=status.value, count=count) for status, count in counts]

def get_vendor_report(db: Session) -> List[VendorReportItem]:
    results = db.query(
        Vendor.name,
        func.count(Invoice.id).label('total_invoices'),
        func.sum(case((Invoice.status == InvoiceStatus.APPROVED, 1), else_=0)).label('approved_invoices'),
        func.sum(case((Invoice.status == InvoiceStatus.REJECTED, 1), else_=0)).label('rejected_invoices')
    ).outerjoin(Invoice, Vendor.id == Invoice.vendor_id).group_by(Vendor.name).all()
    
    return [
        VendorReportItem(
            vendor_name=row.name,
            total_invoices=row.total_invoices or 0,
            approved_invoices=row.approved_invoices or 0,
            rejected_invoices=row.rejected_invoices or 0
        )
        for row in results
    ]

def get_audit_report(
    db: Session, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None, 
    page: int = 1, 
    size: int = 20
) -> PaginatedAuditReport:
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
        
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = []
    for log in logs:
        actor_email = log.actor.email if log.actor else "System"
        items.append(AuditReportItem(
            id=log.id,
            invoice_id=log.invoice_id,
            action=log.action,
            details=log.details,
            actor_email=actor_email,
            timestamp=log.created_at
        ))
        
    return PaginatedAuditReport(
        data=items,
        total=total,
        page=page,
        size=size
    )

def get_approval_report(db: Session, page: int = 1, size: int = 20) -> PaginatedApprovalReport:
    query = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.REJECTED])
    )
    
    total = query.count()
    workflows = query.order_by(ApprovalWorkflow.actioned_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = []
    for wf in workflows:
        approver_email = wf.approver.email if wf.approver else None
        items.append(ApprovalReportItem(
            invoice_id=wf.invoice_id,
            invoice_number=wf.invoice.invoice_number if wf.invoice else "Unknown",
            status=wf.status.value,
            approver_email=approver_email,
            comments=wf.comments,
            actioned_at=wf.actioned_at
        ))
        
    return PaginatedApprovalReport(
        data=items,
        total=total,
        page=page,
        size=size
    )
