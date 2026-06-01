from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import InvoiceStatus

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING_APPROVAL, nullable=False)
    comments = Column(Text)
    actioned_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    invoice = relationship("Invoice", back_populates="workflow")
    approver = relationship("User")
