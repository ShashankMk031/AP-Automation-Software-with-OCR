from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InvoiceStatusReportItem(BaseModel):
    status: str
    count: int

class VendorReportItem(BaseModel):
    vendor_name: str
    total_invoices: int
    approved_invoices: int
    rejected_invoices: int

class AuditReportItem(BaseModel):
    id: int
    invoice_id: int
    action: str
    details: Optional[str] = None
    actor_email: str
    timestamp: datetime

class PaginatedAuditReport(BaseModel):
    data: List[AuditReportItem]
    total: int
    page: int
    size: int

class ApprovalReportItem(BaseModel):
    invoice_id: int
    invoice_number: str
    status: str
    approver_email: Optional[str] = None
    comments: Optional[str] = None
    actioned_at: Optional[datetime] = None

class PaginatedApprovalReport(BaseModel):
    data: List[ApprovalReportItem]
    total: int
    page: int
    size: int

class APAgingReportResponse(BaseModel):
    days_0_30: int
    days_31_60: int
    days_61_90: int
    days_90_plus: int
    total: int

class ExceptionReportItem(BaseModel):
    invoice_number: str
    vendor_name: str
    status: str
    date: Optional[datetime] = None
    failure_reason: Optional[str] = None
    rejection_comments: Optional[str] = None
