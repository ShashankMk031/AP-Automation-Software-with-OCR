from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    invoice_number = Column(String, index=True)
    invoice_date = Column(DateTime)
    subtotal = Column(Float)
    gst_amount = Column(Float)
    total_amount = Column(Float)
    file_path = Column(String)
    status = Column(String, default="pending")
    ocr_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    vendor = relationship("Vendor", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    workflow = relationship("ApprovalWorkflow", back_populates="invoice")
    audit_logs = relationship("AuditLog", back_populates="invoice")

class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    line_total = Column(Float)
    
    invoice = relationship("Invoice", back_populates="line_items")
