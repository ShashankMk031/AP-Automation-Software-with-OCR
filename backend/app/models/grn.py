from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class GRN(Base):
    __tablename__ = "grns"
    
    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String, unique=True, index=True, nullable=False)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    received_amount = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
