from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApprovalActionRequest(BaseModel):
    comments: str

class PendingInvoiceResponse(BaseModel):
    invoice_id: int
    invoice_number: str
    vendor_name: str
    total_amount: float
    status: str

    class Config:
        from_attributes = True

class ApprovalHistoryResponse(BaseModel):
    invoice_id: int
    submitted_at: datetime
    approved_by: Optional[str] = None
    status: str
    comments: Optional[str] = None
    actioned_at: Optional[datetime] = None
