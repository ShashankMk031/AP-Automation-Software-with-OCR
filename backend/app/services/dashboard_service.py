from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.audit import AuditLog
from app.models.user import User
from app.models.enums import InvoiceStatus, VendorStatus
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    VendorSummaryResponse,
    RecentActivityItem,
    OCRMetricsResponse
)

def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    counts = dict(db.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all())
    
    total = sum(counts.values())
    
    return DashboardSummaryResponse(
        total_invoices=total,
        uploaded=counts.get(InvoiceStatus.UPLOADED, 0),
        extracted=counts.get(InvoiceStatus.EXTRACTED, 0),
        validation_passed=counts.get(InvoiceStatus.VALIDATION_PASSED, 0),
        validation_failed=counts.get(InvoiceStatus.VALIDATION_FAILED, 0),
        pending_approval=counts.get(InvoiceStatus.PENDING_APPROVAL, 0),
        approved=counts.get(InvoiceStatus.APPROVED, 0),
        rejected=counts.get(InvoiceStatus.REJECTED, 0)
    )

def get_vendor_summary(db: Session) -> VendorSummaryResponse:
    counts = dict(db.query(Vendor.status, func.count(Vendor.id)).group_by(Vendor.status).all())
    
    total = sum(counts.values())
    
    return VendorSummaryResponse(
        total_vendors=total,
        active_vendors=counts.get(VendorStatus.ACTIVE, 0),
        inactive_vendors=counts.get(VendorStatus.INACTIVE, 0)
    )

def get_recent_activity(db: Session, limit: int = 20) -> list[RecentActivityItem]:
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    
    results = []
    for log in logs:
        actor_email = log.actor.email if log.actor else "System"
        results.append(RecentActivityItem(
            action=log.action,
            timestamp=log.created_at,
            actor=actor_email,
            details=log.details
        ))
    return results

def get_ocr_metrics(db: Session) -> OCRMetricsResponse:
    # OCR Confidence
    ocr_stats = db.query(
        func.count(Invoice.id).label('total_processed'),
        func.avg(Invoice.ocr_confidence).label('avg_confidence')
    ).filter(Invoice.ocr_confidence.isnot(None)).first()
    
    total_processed = ocr_stats.total_processed or 0
    avg_conf = float(ocr_stats.avg_confidence or 0.0)
    
    # Validation Rate
    passed = db.query(func.count(Invoice.id)).filter(
        Invoice.status.in_([
            InvoiceStatus.VALIDATION_PASSED, 
            InvoiceStatus.PENDING_APPROVAL, 
            InvoiceStatus.APPROVED, 
            InvoiceStatus.REJECTED
        ])
    ).scalar() or 0
    
    failed = db.query(func.count(Invoice.id)).filter(
        Invoice.status == InvoiceStatus.VALIDATION_FAILED
    ).scalar() or 0
    
    total_validated = passed + failed
    success_rate = (passed / total_validated * 100.0) if total_validated > 0 else 0.0
    
    return OCRMetricsResponse(
        total_processed=total_processed,
        avg_ocr_confidence=round(avg_conf, 4),
        validation_success_rate=round(success_rate, 2)
    )
