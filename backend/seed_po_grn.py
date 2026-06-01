import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.grn import GRN

def seed_pos_and_grns():
    db: Session = SessionLocal()
    
    # We need vendors to associate POs with
    vendors = db.query(Vendor).all()
    if not vendors or len(vendors) < 5:
        print("Not enough vendors found. Please run seed_vendors.py first.")
        db.close()
        return

    # Seed Purchase Orders
    po_data_list = [
        {"po_number": "PO-2023-001", "vendor_id": vendors[0].id, "amount": 150000.0, "status": "active"},
        {"po_number": "PO-2023-002", "vendor_id": vendors[1].id, "amount": 250000.50, "status": "active"},
        {"po_number": "PO-2023-003", "vendor_id": vendors[2].id, "amount": 75000.0, "status": "active"},
        {"po_number": "PO-2023-004", "vendor_id": vendors[3].id, "amount": 500000.0, "status": "active"},
        {"po_number": "PO-2023-005", "vendor_id": vendors[4].id, "amount": 320000.75, "status": "active"}
    ]

    created_pos = []
    for po_data in po_data_list:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_data["po_number"]).first()
        if not po:
            new_po = PurchaseOrder(**po_data)
            db.add(new_po)
            db.flush() # flush to get the ID for GRN
            created_pos.append(new_po)
            print(f"Created PO: {po_data['po_number']}")
        else:
            created_pos.append(po)
            print(f"PO already exists: {po_data['po_number']}")
            
    # Seed GRNs
    grn_data_list = [
        {"grn_number": "GRN-2023-001", "po_id": created_pos[0].id, "received_amount": 150000.0},
        {"grn_number": "GRN-2023-002", "po_id": created_pos[1].id, "received_amount": 100000.0}, # Partial receipt
        {"grn_number": "GRN-2023-003", "po_id": created_pos[2].id, "received_amount": 75000.0},
        {"grn_number": "GRN-2023-004", "po_id": created_pos[3].id, "received_amount": 500000.0},
        {"grn_number": "GRN-2023-005", "po_id": created_pos[4].id, "received_amount": 150000.0} # Partial receipt
    ]
    
    for grn_data in grn_data_list:
        grn = db.query(GRN).filter(GRN.grn_number == grn_data["grn_number"]).first()
        if not grn:
            new_grn = GRN(**grn_data)
            db.add(new_grn)
            print(f"Created GRN: {grn_data['grn_number']}")
        else:
            print(f"GRN already exists: {grn_data['grn_number']}")

    db.commit()
    db.close()
    print("PO and GRN seeding completed.")

if __name__ == "__main__":
    seed_pos_and_grns()
