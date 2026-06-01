import sys
import os

sys.path.append("/Users/shashankmk/Documents/Projects-Development/AP-Automation-Software-with-OCR/backend")

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.vendor import Vendor
from app.models.audit import AuditLog
from app.core import security
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.services import vendor_service

def run_tests():
    db = SessionLocal()
    print("Executing custom API integration tests...")

    # 1. Verify User login capabilities
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    finance = db.query(User).filter(User.email == "finance@example.com").first()
    
    assert admin is not None, "Admin user must exist from database seeding"
    assert finance is not None, "Finance user must exist from database seeding"
    
    print("Seeded users exist correctly.")

    # Test password verification
    assert security.verify_password("password123", admin.password_hash), "Password verification failed"
    print("Password verification succeeded.")

    # 2. Test Vendor CRUD operations + automated Audit Logs via service layer
    vendor_data = VendorCreate(
        name="Test Vendor Inc",
        gstin="27AADCA1111A1Z1",
        bank_details="{}",
    )

    # Let's delete if already exists to make test idempotent
    existing = db.query(Vendor).filter(Vendor.gstin == "27AADCA1111A1Z1").first()
    if existing:
        db.delete(existing)
        db.commit()

    # Create vendor
    new_vendor = vendor_service.create_vendor(db=db, vendor_in=vendor_data, current_user=admin)
    assert new_vendor.id is not None, "Vendor creation failed"
    print(f"Created vendor: {new_vendor.name} (ID: {new_vendor.id})")

    # Verify Audit log was created automatically
    audit = db.query(AuditLog).filter(AuditLog.action == "Vendor Created").order_by(AuditLog.created_at.desc()).first()
    assert audit is not None, "Automatic Audit Log for creation not found"
    assert audit.actor_id == admin.id, "Actor ID mismatch on Audit Log"
    print("Vendor creation automatic Audit Log verified successfully.")

    # Update vendor
    update_data = VendorUpdate(name="Test Vendor Updated")
    updated_vendor = vendor_service.update_vendor(db=db, vendor_id=new_vendor.id, vendor_in=update_data, current_user=admin)
    assert updated_vendor.name == "Test Vendor Updated", "Vendor update failed"
    print(f"Updated vendor name to: {updated_vendor.name}")

    # Verify Audit log for update
    audit_upd = db.query(AuditLog).filter(AuditLog.action == "Vendor Updated").order_by(AuditLog.created_at.desc()).first()
    assert audit_upd is not None, "Automatic Audit Log for update not found"
    print("Vendor update automatic Audit Log verified successfully.")

    # Search and pagination
    vendors, total = vendor_service.get_vendors(db=db, page=1, limit=5, search="Updated")
    assert total >= 1, "Vendor search failed"
    assert vendors[0].name == "Test Vendor Updated", "Search matching vendor mismatch"
    print(f"Vendor search and pagination matched '{vendors[0].name}' successfully.")

    # Soft delete (deactivation)
    deactivated = vendor_service.deactivate_vendor(db=db, vendor_id=new_vendor.id, current_user=admin)
    assert deactivated.status == "INACTIVE", "Vendor soft-delete deactivation failed"
    print("Vendor soft-deactivated successfully.")

    # Verify Audit log for deactivation
    audit_deact = db.query(AuditLog).filter(AuditLog.action == "Vendor Deactivated").order_by(AuditLog.created_at.desc()).first()
    assert audit_deact is not None, "Automatic Audit Log for deactivation not found"
    print("Vendor deactivation automatic Audit Log verified successfully.")

    # Clean up test vendor and audit logs to keep database fresh
    db.delete(deactivated)
    # also clean logs
    db.query(AuditLog).filter(AuditLog.actor_id == admin.id, AuditLog.action.in_(["Vendor Created", "Vendor Updated", "Vendor Deactivated"])).delete()
    db.commit()
    db.close()
    print("Integration tests completed successfully!")

if __name__ == "__main__":
    run_tests()