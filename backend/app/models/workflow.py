from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    comments = Column(Text)
    actioned_at = Column(DateTime(timezone=True))
    
    invoice = relationship("Invoice", back_populates="workflow")
    approver = relationship("User")
