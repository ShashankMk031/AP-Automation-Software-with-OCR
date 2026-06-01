from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class GRN(Base):
    __tablename__ = "grns"
    
    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String, unique=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    received_amount = Column(Float)
    
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
