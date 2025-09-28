from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.db.session import get_db
from app.db.models.order import Order
from app.db.models.order_item import OrderItem
from app.db.models.vendor import Vendor
from app.schemas.order import OrderCreate, OrderResponse, OrderPriority, OrderSummaryResponse, PaginatedOrderResponse
from app.background.order_processing import process_order_background, process_high_priority_order
from typing import List, Optional, Union
from datetime import datetime, date, time
from fastapi import Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    
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

    if order.priority == OrderPriority.HIGH:
        background_tasks.add_task(process_high_priority_order, new_order.id)
        logger.info(f"Queued HIGH PRIORITY order {new_order.order_id} (ID: {new_order.id}) for processing")
    else:
        background_tasks.add_task(process_order_background, new_order.id)
        logger.info(f"📋 Queued order {new_order.order_id} (ID: {new_order.id}) for background processing")

    return new_order

@router.get("/{vendor_id}", response_model=Union[List[OrderResponse], PaginatedOrderResponse])
def get_orders(vendor_id: int, start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"), end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"), priority: Optional[OrderPriority] = Query(None),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"), 
    db: Session = Depends(get_db)
):
    query = db.query(Order).filter(Order.vendor_id == vendor_id)

    if start_date:
        start_datetime = datetime.combine(start_date, time.min)
        query = query.filter(Order.created_at >= start_datetime)
    if end_date:
        end_datetime = datetime.combine(end_date, time.max)
        query = query.filter(Order.created_at <= end_datetime)

    if priority:
        query = query.filter(Order.priority == priority)

    total_count = query.count()
    
    if total_count == 0:
        raise HTTPException(status_code=404, detail="No orders found for this vendor")

    query = query.order_by(
        case(
            (Order.priority == OrderPriority.HIGH, 1),
            (Order.priority == OrderPriority.MEDIUM, 2),
            (Order.priority == OrderPriority.LOW, 3),
            else_=4
        ),
        Order.created_at
    )

    if total_count > 50:
        params = Params(page=page, size=size)
        paginated_result = paginate(query, params)
        return paginated_result
    else:
        orders = query.all()
        return orders

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
