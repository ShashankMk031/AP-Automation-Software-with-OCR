import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core import security
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorPaginationResponse
)
from app.services import vendor_service

router = APIRouter()

# Role Dependencies
admin_only = security.require_role([UserRole.ADMIN])
all_roles = security.require_role([UserRole.ADMIN, UserRole.FINANCE, UserRole.APPROVER])

@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_new_vendor(
    vendor_in: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    return vendor_service.create_vendor(db=db, vendor_in=vendor_in, current_user=current_user)

@router.get("", response_model=VendorPaginationResponse)
def read_vendors(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(all_roles)
):
    items, total = vendor_service.get_vendors(db=db, page=page, limit=limit, search=search)
    pages = math.ceil(total / limit) if total > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

@router.get("/{vendor_id}", response_model=VendorResponse)
def read_vendor_by_id(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_roles)
):
    vendor = vendor_service.get_vendor(db=db, vendor_id=vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    return vendor

@router.put("/{vendor_id}", response_model=VendorResponse)
def update_existing_vendor(
    vendor_id: int,
    vendor_in: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    vendor = vendor_service.update_vendor(db=db, vendor_id=vendor_id, vendor_in=vendor_in, current_user=current_user)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    return vendor

@router.delete("/{vendor_id}", response_model=VendorResponse)
def delete_vendor_soft(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    vendor = vendor_service.deactivate_vendor(db=db, vendor_id=vendor_id, current_user=current_user)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    return vendor
