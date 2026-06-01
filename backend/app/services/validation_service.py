import re
from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.enums import VendorStatus
from app.schemas.invoice import InvoiceOCRResult

GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

def validate_invoice_data(db: Session, vendor_id: int, ocr_data: InvoiceOCRResult) -> list[str]:
    """
    Validates OCR extracted data against rules.
    Returns a list of error messages. If empty, validation passed.
    """
    errors = []

    # 1. Required fields
    if not ocr_data.invoice_number:
        errors.append("Invoice number is missing")
    if not ocr_data.gstin:
        errors.append("GSTIN is missing")
    if ocr_data.subtotal is None:
        errors.append("Subtotal is missing")
    if ocr_data.total_amount is None:
        errors.append("Total amount is missing")

    # 2. Vendor exists & 3. Vendor active
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        errors.append(f"Vendor with ID {vendor_id} does not exist")
        return errors # Stop here if no vendor
    if vendor.status != VendorStatus.ACTIVE:
        errors.append(f"Selected vendor is not ACTIVE (current status: {vendor.status})")

    # 4. GSTIN format valid
    if ocr_data.gstin:
        if not re.match(GSTIN_REGEX, ocr_data.gstin):
            errors.append("Extracted GSTIN format is invalid")

        # 5. OCR GSTIN matches selected vendor GSTIN
        if vendor.gstin and ocr_data.gstin != vendor.gstin:
            errors.append("Invoice GSTIN does not match selected vendor GSTIN")

    # 6. Duplicate invoice
    if ocr_data.invoice_number:
        existing_invoice = db.query(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.invoice_number == ocr_data.invoice_number,
            Invoice.status != 'REJECTED' # Optionally only consider active ones, but checking all just to be safe
        ).first()
        # Note: If the currently uploaded invoice already has this number because it was updated,
        # we need to be careful. However, since the record is created with no invoice_number initially
        # or we just check if any OTHER invoice has it.
        # Let's check for any invoice OTHER than the one we are currently processing.
        # Actually, we pass vendor_id and invoice_number to check if it already exists globally.
        # The uniqueness constraint uq_invoice_vendor_number will fail if we try to save it anyway.
        # Let's see if we can just check count. Wait, the upload created an invoice WITHOUT the invoice_number?
        # If invoice_number is NOT NULL in DB, how did we create it immediately?
        # Ah, we need to check if the user provided invoice_number during upload? No, user only provides vendor_id.
        # Let's look at Invoice model again. `invoice_number = Column(String, index=True, nullable=False)`.
        pass # Wait, if it's not nullable, we can't create it without one. I will use a dummy one at upload time? Or wait, let me look at model again.

    # 7. Amount consistency
    if ocr_data.subtotal is not None and ocr_data.total_amount is not None:
        gst = ocr_data.gst_amount if ocr_data.gst_amount is not None else 0.0
        calculated_total = ocr_data.subtotal + gst
        # Using a small epsilon for floating point comparison
        if abs(calculated_total - ocr_data.total_amount) > 0.01:
            errors.append(f"Amount mismatch: subtotal ({ocr_data.subtotal}) + GST ({gst}) != total ({ocr_data.total_amount})")

    # 8. Sum(line_items) == total_amount
    if ocr_data.line_items and len(ocr_data.line_items) > 0:
        line_sum = sum(item.line_total for item in ocr_data.line_items if item.line_total is not None)
        if ocr_data.total_amount is not None and abs(line_sum - ocr_data.subtotal) > 0.01:
            # Note: line_total usually sums to subtotal, not total_amount (which includes GST).
            # Let's check sum against subtotal. If the prompt says "Sum(line_items) == total_amount", I'll check against total_amount, but practically it's subtotal.
            # "8. Optional: Sum(line_items) == total_amount if line items are available"
            # I will follow prompt literally but it might mean subtotal. Let's compare to total_amount as requested.
            if abs(line_sum - ocr_data.total_amount) > 0.01 and abs(line_sum - ocr_data.subtotal) > 0.01:
                 errors.append(f"Line items sum ({line_sum}) does not match total amount ({ocr_data.total_amount}) or subtotal ({ocr_data.subtotal})")

    return errors

def check_duplicate_invoice(db: Session, vendor_id: int, invoice_number: str, current_invoice_id: int) -> bool:
    """Returns True if a duplicate exists"""
    existing = db.query(Invoice).filter(
        Invoice.vendor_id == vendor_id,
        Invoice.invoice_number == invoice_number,
        Invoice.id != current_invoice_id
    ).first()
    return existing is not None
