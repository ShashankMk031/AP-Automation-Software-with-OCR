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
    PaginatedApprovalReport,
    APAgingReportResponse,
    ExceptionReportItem
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

def get_ap_aging_report(db: Session) -> APAgingReportResponse:
    invoices = db.query(Invoice.invoice_date).filter(
        Invoice.status.in_([
            InvoiceStatus.VALIDATION_PASSED,
            InvoiceStatus.PENDING_APPROVAL,
            InvoiceStatus.APPROVED
        ]),
        Invoice.invoice_date.isnot(None)
    ).all()
    
    res = {
        "days_0_30": 0,
        "days_31_60": 0,
        "days_61_90": 0,
        "days_90_plus": 0,
        "total": 0
    }
    
    today = datetime.now().date()
    
    for row in invoices:
        inv_date = row.invoice_date
        if not inv_date:
            continue
            
        age_days = (today - inv_date.date()).days
        
        # Invoices can be future dated, treat age < 0 as 0
        if age_days < 0:
            age_days = 0
            
        if age_days <= 30:
            res["days_0_30"] += 1
        elif age_days <= 60:
            res["days_31_60"] += 1
        elif age_days <= 90:
            res["days_61_90"] += 1
        else:
            res["days_90_plus"] += 1
            
        res["total"] += 1
        
    return APAgingReportResponse(**res)

def get_exception_report(db: Session) -> List[ExceptionReportItem]:
    invoices = db.query(Invoice).filter(
        Invoice.status.in_([
            InvoiceStatus.VALIDATION_FAILED,
            InvoiceStatus.REJECTED
        ])
    ).all()
    
    results = []
    for inv in invoices:
        failure_reason = None
        rejection_comments = None
        
        if inv.status == InvoiceStatus.VALIDATION_FAILED:
            for log in sorted(inv.audit_logs, key=lambda x: x.timestamp, reverse=True):
                if log.action in ('VALIDATION_FAILED', 'OCR_FAILED', 'DUPLICATE_DETECTED'):
                    failure_reason = log.details
                    break
        elif inv.status == InvoiceStatus.REJECTED:
            if inv.workflow:
                rejection_comments = inv.workflow.comments
                
        results.append(ExceptionReportItem(
            invoice_number=inv.invoice_number,
            vendor_name=inv.vendor.name if inv.vendor else "Unknown",
            status=inv.status.value,
            date=inv.invoice_date or inv.created_at,
            failure_reason=failure_reason,
            rejection_comments=rejection_comments
        ))
    
    return results
