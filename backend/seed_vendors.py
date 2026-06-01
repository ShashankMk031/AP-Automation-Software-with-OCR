import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.vendor import Vendor
from app.models.enums import VendorStatus

def seed_vendors():
    db: Session = SessionLocal()
    
    vendors = [
        {
            "name": "Acme Corp",
            "gstin": "27AADCA1111A1Z1",
            "bank_details": json.dumps({"bank": "HDFC Bank", "account_no": "1234567890", "ifsc": "HDFC0001234"}),
            "status": VendorStatus.ACTIVE
        },
        {
            "name": "Global Tech Solutions",
            "gstin": "29BBDFG2222B2Z2",
            "bank_details": json.dumps({"bank": "ICICI Bank", "account_no": "0987654321", "ifsc": "ICIC0005678"}),
            "status": VendorStatus.ACTIVE
        },
        {
            "name": "Omega Industries",
            "gstin": "07CCDEF3333C3Z3",
            "bank_details": json.dumps({"bank": "State Bank of India", "account_no": "1122334455", "ifsc": "SBIN0009876"}),
            "status": VendorStatus.ACTIVE
        },
        {
            "name": "NextGen Supplies",
            "gstin": "33DDGHI4444D4Z4",
            "bank_details": json.dumps({"bank": "Axis Bank", "account_no": "5566778899", "ifsc": "UTIB0003456"}),
            "status": VendorStatus.ACTIVE
        },
        {
            "name": "Pioneer Logistics",
            "gstin": "19EEJKL5555E5Z5",
            "bank_details": json.dumps({"bank": "Kotak Mahindra Bank", "account_no": "9988776655", "ifsc": "KKBK0001234"}),
            "status": VendorStatus.ACTIVE
        }
    ]

    for vendor_data in vendors:
        vendor = db.query(Vendor).filter(Vendor.gstin == vendor_data["gstin"]).first()
        if not vendor:
            new_vendor = Vendor(**vendor_data)
            db.add(new_vendor)
            print(f"Created vendor: {vendor_data['name']}")
        else:
            vendor.status = vendor_data["status"]
            db.add(vendor)
            print(f"Vendor already exists, updated status: {vendor_data['name']}")
            
    db.commit()
    db.close()
    print("Vendor seeding completed.")

if __name__ == "__main__":
    seed_vendors()
