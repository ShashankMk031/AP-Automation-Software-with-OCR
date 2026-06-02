from pydantic import BaseModel
from typing import List, Optional

class POMatchRequest(BaseModel):
    po_id: int

class POMatchResponse(BaseModel):
    match_type: str
    result: str
    vendor_match: bool
    po_amount: float
    grn_amount: Optional[float] = None
    invoice_amount: float
    tolerance: float = 0.01
    details: List[str] = []
