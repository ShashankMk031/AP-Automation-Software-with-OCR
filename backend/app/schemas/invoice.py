from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.enums import InvoiceStatus

class InvoiceLineItemOCR(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None

class InvoiceOCRResult(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    gstin: Optional[str] = None
    invoice_date: Optional[str] = None # Keeping string to handle OCR variations, will parse later if needed
    subtotal: Optional[float] = None
    gst_amount: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: List[InvoiceLineItemOCR] = []

class InvoiceProcessingSummary(BaseModel):
    invoice_id: int
    status: InvoiceStatus
    ocr_data: Optional[InvoiceOCRResult] = None
    validation_errors: List[str] = []

class InvoiceResponse(BaseModel):
    id: int
    vendor_id: int
    invoice_number: str
    invoice_date: Optional[datetime] = None
    subtotal: Optional[float] = None
    gst_amount: Optional[float] = None
    total_amount: Optional[float] = None
    file_path: Optional[str] = None
    status: InvoiceStatus
    ocr_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class PaginatedInvoiceResponse(BaseModel):
    data: List[InvoiceResponse]
    total: int
    page: int
    size: int

class InvoiceDetailResponse(BaseModel):
    invoice: InvoiceResponse
    vendor_name: str
    line_items: List[InvoiceLineItemOCR]
    approval_history: list
    audit_logs: list
