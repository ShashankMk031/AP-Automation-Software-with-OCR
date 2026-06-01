import json
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from fastapi import HTTPException, status

from app.models.vendor import Vendor
from app.models.enums import VendorStatus
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.vendor import VendorCreate, VendorUpdate

def create_vendor(db: Session, vendor_in: VendorCreate, current_user: User) -> Vendor:
    # Check duplicate GSTIN
    existing = db.query(Vendor).filter(Vendor.gstin == vendor_in.gstin).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor with GSTIN '{vendor_in.gstin}' already exists."
        )
    
    vendor = Vendor(
        name=vendor_in.name,
        gstin=vendor_in.gstin,
        bank_details=vendor_in.bank_details,
        status=vendor_in.status
    )
    db.add(vendor)
    db.flush()  # to get vendor.id

    # Create Audit Log
    audit_details = {
        "name": vendor.name,
        "gstin": vendor.gstin,
        "status": vendor.status.value
    }
    audit = AuditLog(
        action="Vendor Created",
        actor_id=current_user.id,
        details=json.dumps(audit_details)
    )
    db.add(audit)
    db.commit()
    db.refresh(vendor)
    return vendor

def update_vendor(db: Session, vendor_id: int, vendor_in: VendorUpdate, current_user: User) -> Optional[Vendor]:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    
    # Check duplicate GSTIN if being updated
    if vendor_in.gstin and vendor_in.gstin != vendor.gstin:
        existing = db.query(Vendor).filter(Vendor.gstin == vendor_in.gstin).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another vendor with GSTIN '{vendor_in.gstin}' already exists."
            )
            
    # Track changes for Audit Log
    changes = {}
    update_data = vendor_in.model_dump(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(vendor, field)
        if old_value != new_value:
            changes[field] = {
                "old": old_value.value if hasattr(old_value, 'value') else old_value,
                "new": new_value.value if hasattr(new_value, 'value') else new_value
            }
            setattr(vendor, field, new_value)
            
    if changes:
        # Create Audit Log
        audit = AuditLog(
            action="Vendor Updated",
            actor_id=current_user.id,
            details=json.dumps({"vendor_id": vendor_id, "changes": changes})
        )
        db.add(audit)
        db.commit()
        db.refresh(vendor)
        
    return vendor

def deactivate_vendor(db: Session, vendor_id: int, current_user: User) -> Optional[Vendor]:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
        
    if vendor.status != VendorStatus.INACTIVE:
        vendor.status = VendorStatus.INACTIVE
        # Create Audit Log
        audit = AuditLog(
            action="Vendor Deactivated",
            actor_id=current_user.id,
            details=json.dumps({"vendor_id": vendor_id, "name": vendor.name})
        )
        db.add(audit)
        db.commit()
        db.refresh(vendor)
        
    return vendor

def get_vendor(db: Session, vendor_id: int) -> Optional[Vendor]:
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()

def get_vendors(db: Session, page: int = 1, limit: int = 20, search: Optional[str] = None) -> Tuple[List[Vendor], int]:
    query = db.query(Vendor)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Vendor.name.ilike(search_filter),
                Vendor.gstin.ilike(search_filter)
            )
        )
    
    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(desc(Vendor.created_at)).offset(offset).limit(limit).all()
    return items, total
