from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardSummaryResponse(BaseModel):
    total_invoices: int
    uploaded: int
    extracted: int
    validation_passed: int
    validation_failed: int
    pending_approval: int
    approved: int
    rejected: int

class VendorSummaryResponse(BaseModel):
    total_vendors: int
    active_vendors: int
    inactive_vendors: int

class RecentActivityItem(BaseModel):
    action: str
    timestamp: datetime
    actor: Optional[str] = None
    details: Optional[str] = None

class OCRMetricsResponse(BaseModel):
    total_processed: int
    avg_ocr_confidence: float
    validation_success_rate: float
