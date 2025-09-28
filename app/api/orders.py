from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.order import Order
from app.db.models.order_item import OrderItem
from app.db.models.vendor import Vendor
from app.schemas.order import OrderCreate, OrderResponse, OrderPriority, OrderSummaryResponse
from typing import List, Optional
from datetime import datetime
from fastapi import Query

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):

    vendor = db.query(Vendor).filter(Vendor.id == order.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    existing_order = db.query(Order).filter(
        Order.order_id == order.order_id,
        Order.vendor_id == order.vendor_id
    ).first()

    if existing_order:
        raise HTTPException(status_code=409, detail="Duplicate order for this vendor")


    new_order = Order(
        order_id=order.order_id,
        vendor_id=order.vendor_id,
        priority=order.priority,
        address=order.address,
        city=order.city,
        state=order.state,
        postal_code=order.postal_code
    )

 
    for item in order.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Quantity must be >0 for item {item.item_name}")

        new_item = OrderItem(
            item_name=item.item_name,
            quantity=item.quantity
        )
        new_order.items.append(new_item)

  
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order

@router.get("/{vendor_id}", response_model=List[OrderResponse])
def get_orders( vendor_id: int,  start_date: Optional[datetime] = Query(None), end_date: Optional[datetime] = Query(None), priority: Optional[OrderPriority] = Query(None), db: Session = Depends(get_db)):

    query = db.query(Order).filter(Order.vendor_id == vendor_id)

    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    if priority:
        query = query.filter(Order.priority == priority)

    orders = query.all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this vendor")

    priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    orders_sorted = sorted(
        orders,
        key=lambda o: (priority_order[o.priority.value], o.created_at)
    )

    return orders_sorted

@router.get("/status/{order_id}")
def get_order_status(order_id: str, db: Session = Depends(get_db)):
    
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.order_id,
        "status": order.status,
        "updated_at": order.updated_at
    } 

@router.get("/summary/{vendor_id}", response_model=OrderSummaryResponse)
def get_order_summary(vendor_id: int, db: Session = Depends(get_db)):
   
    orders = db.query(Order).filter(Order.vendor_id == vendor_id).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this vendor")

    total_orders = len(orders)

    total_items = db.query(func.sum(OrderItem.quantity)).join(Order).filter(
        Order.vendor_id == vendor_id
    ).scalar() or 0

    total_priority_orders = db.query(func.count(Order.id)).filter(
        Order.vendor_id == vendor_id,
        Order.priority == OrderPriority.HIGH
    ).scalar() or 0

    return {
        "total_orders": total_orders,
        "total_items": total_items,
        "total_priority_orders": total_priority_orders
    }
