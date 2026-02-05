"""Payment method database model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PaymentMethod(Base):
    """Payment method model."""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_method_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # card, bank_transfer, electronic, etc.
    details = Column(JSON)  # Store payment method details as JSON
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

