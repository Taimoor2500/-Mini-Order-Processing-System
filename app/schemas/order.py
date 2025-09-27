# app/schemas/order.py
from typing import List, Optional
from pydantic import BaseModel, conint, validator
from enum import Enum
from .vendor import VendorResponse

class OrderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"



class OrderItemCreate(BaseModel):
    item_name: str
    quantity: conint(gt=0)

class OrderItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    order_id: str
    vendor_id: int
    priority: Optional[OrderPriority] = OrderPriority.LOW
    items: List[OrderItemCreate]

    address: str
    city: str
    state: str
    postal_code: str

    @validator("address", "city", "state", "postal_code")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @validator("postal_code")
    def postal_code_length(cls, v):
        if len(v.strip()) < 4:
            raise ValueError("Postal code too short")
        return v


class OrderResponse(BaseModel):
    id: int
    order_id: str
    vendor: VendorResponse
    priority: OrderPriority
    status: str
    items: List[OrderItemResponse]
    
    address: str
    city: str
    state: str
    postal_code: str

    class Config:
        orm_mode = True


class OrderSummaryResponse(BaseModel):
    total_orders: int
    total_items: int
    total_priority_orders: int
