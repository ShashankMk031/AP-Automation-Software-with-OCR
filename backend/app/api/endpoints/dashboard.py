from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    VendorSummaryResponse,
    RecentActivityItem,
    OCRMetricsResponse
)
from app.services.dashboard_service import (
    get_dashboard_summary,
    get_vendor_summary,
    get_recent_activity,
    get_ocr_metrics
)

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves high-level summary metrics for all invoices across the system.
    """
    return get_dashboard_summary(db)

@router.get("/vendor-summary", response_model=VendorSummaryResponse)
def get_vendor_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves summary metrics for vendors in the system.
    """
    return get_vendor_summary(db)

@router.get("/recent-activity", response_model=List[RecentActivityItem])
def get_recent_activity_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the latest 20 audit log entries.
    """
    return get_recent_activity(db, limit=20)

@router.get("/ocr-metrics", response_model=OCRMetricsResponse)
def get_ocr_metrics_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves aggregated OCR extraction and validation success metrics.
    """
    return get_ocr_metrics(db)
