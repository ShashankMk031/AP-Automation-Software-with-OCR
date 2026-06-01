import re
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.enums import VendorStatus

# 15-character Indian GSTIN alphanumeric regex pattern
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

class VendorBase(BaseModel):
    name: str
    gstin: str
    bank_details: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE

class VendorCreate(VendorBase):
    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if not GSTIN_REGEX.match(v_upper):
            raise ValueError("Invalid GSTIN format. Must be a valid 15-character Indian GSTIN.")
        return v_upper

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    bank_details: Optional[str] = None
    status: Optional[VendorStatus] = None

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_upper = v.upper().strip()
        if not GSTIN_REGEX.match(v_upper):
            raise ValueError("Invalid GSTIN format. Must be a valid 15-character Indian GSTIN.")
        return v_upper

class VendorResponse(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VendorPaginationResponse(BaseModel):
    items: List[VendorResponse]
    total: int
    page: int
    limit: int
    pages: int
