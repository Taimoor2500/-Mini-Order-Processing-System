# app/schemas/order_item.py
from pydantic import BaseModel, conint

class OrderItemCreate(BaseModel):
    item_name: str
    quantity: conint(gt=0)

class OrderItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int

    class Config:
        orm_mode = True
