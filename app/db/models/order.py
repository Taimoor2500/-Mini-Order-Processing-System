# app/db/models/order.py
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class OrderPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    priority = Column(Enum(OrderPriority), default=OrderPriority.LOW, nullable=False)
    status = Column(String, default="pending")
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("uq_order_vendor", "order_id", "vendor_id", unique=True),
        Index("ix_vendor_id", "vendor_id"),
        Index("ix_priority", "priority"),
        Index("ix_created_at", "created_at"),
    )
