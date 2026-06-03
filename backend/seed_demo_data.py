import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.grn import GRN
from app.models.enums import VendorStatus, PurchaseOrderStatus

def seed_data():
    db = SessionLocal()
    try:
        print("Starting data reset...")
        # Step 1 - Clear business data and reset sequences
        # Ordered appropriately for FK constraints
        db.execute(text("""
            TRUNCATE TABLE 
                audit_logs, 
                approval_workflows, 
                invoice_line_items, 
                invoices, 
                grns, 
                purchase_orders, 
                vendors 
            RESTART IDENTITY CASCADE;
        """))
        db.commit()
        print("Data cleared successfully.")

        # Step 2 - Create 10 Vendors
        print("Seeding vendors...")
        vendors = []
        for i in range(1, 11):
            vendor = Vendor(
                name=f"Vendor{i}",
                gstin=f"29ABCDE10{i:02d}F1Z5",
                status=VendorStatus.ACTIVE,
                bank_details='{"Bank": "Demo Bank", "Branch": "Bangalore", "Account Number": "' + f"1000{i:04d}" + '", "IFSC": "DEMO0001234"}'
            )
            vendors.append(vendor)
            db.add(vendor)
        db.commit()

        # Refresh to get IDs
        for v in vendors:
            db.refresh(v)

        # Step 3 - Create Purchase Orders
        print("Seeding purchase orders...")
        pos = []
        for i, vendor in enumerate(vendors, start=1):
            po = PurchaseOrder(
                po_number=f"PO-10{i:02d}",
                vendor_id=vendor.id,
                amount=(11800 * i),
                status=PurchaseOrderStatus.OPEN
            )
            pos.append(po)
            db.add(po)
        db.commit()

        for po in pos:
            db.refresh(po)

        # Step 4 - Create GRNs for Vendor 8, 9, 10
        print("Seeding GRNs...")
        grn_vendors = [8, 9, 10]
        grns = []
        for i in grn_vendors:
            po = pos[i-1] # 0-indexed
            grn = GRN(
                grn_number=f"GRN-10{i:02d}",
                po_id=po.id,
                received_amount=po.amount
            )
            grns.append(grn)
            db.add(grn)
        db.commit()
        
        for g in grns:
            db.refresh(g)

        # Step 5 - Verify Database Counts
        print("\n--- STEP 5: VERIFICATION ---")
        vendor_count = db.execute(text("SELECT COUNT(*) FROM vendors")).scalar()
        po_count = db.execute(text("SELECT COUNT(*) FROM purchase_orders")).scalar()
        grn_count = db.execute(text("SELECT COUNT(*) FROM grns")).scalar()

        print(f"vendors = {vendor_count}")
        print(f"purchase_orders = {po_count}")
        print(f"grns = {grn_count}")

        # Step 7 - Output Reference Table
        print("\n--- STEP 7: REFERENCE TABLE ---")
        for i, vendor in enumerate(vendors):
            po = pos[i]
            grn = next((g for g in grns if g.po_id == po.id), None)
            
            print(f"{vendor.name}")
            print(f"GSTIN: {vendor.gstin}")
            print(f"PO: {po.po_number}")
            if grn:
                print(f"GRN: {grn.grn_number}")
            print(f"Amount: {po.amount}")
            print()

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
