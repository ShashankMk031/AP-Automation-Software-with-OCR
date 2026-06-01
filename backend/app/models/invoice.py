from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import InvoiceStatus

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    invoice_number = Column(String, index=True, nullable=False)
    invoice_date = Column(DateTime(timezone=True))
    subtotal = Column(Float)
    gst_amount = Column(Float)
    total_amount = Column(Float)
    file_path = Column(String)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UPLOADED, nullable=False)
    ocr_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    vendor = relationship("Vendor", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    workflow = relationship("ApprovalWorkflow", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("vendor_id", "invoice_number", name="uq_invoice_vendor_number"),
    )

class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    line_total = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    invoice = relationship("Invoice", back_populates="line_items")
