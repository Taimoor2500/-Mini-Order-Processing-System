import asyncio
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.order import Order, OrderStatus

logger = logging.getLogger(__name__)

async def process_order_background(order_id: int):
    logger.info(f"Starting background processing for order ID: {order_id}")
    
    db = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        order.status = OrderStatus.PROCESSING
        db.commit()
        logger.info(f"Processing order {order.order_id} - Status: {order.status.value}")
        
        processing_steps = [
            "Validating order details and customer information",
            "Checking inventory availability for all items", 
            "Calculating shipping costs and delivery time",
            "Processing payment authorization",
            "Sending order confirmation email to customer",
            "Updating order status to processed"
        ]
        
        for i, step in enumerate(processing_steps, 1):
            logger.info(f"Step {i}/{len(processing_steps)}: {step}")
            await asyncio.sleep(2)
            logger.info(f"Completed step {i}: {step}")
        
        order.status = OrderStatus.PROCESSED
        db.commit()
        logger.info(f"Order {order.order_id} - Status: {order.status.value}")
        
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {e}")
        
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.FAILED
                db.commit()
                logger.info(f"Order {order.order_id} - Status: {order.status.value}")
        except Exception as db_error:
            logger.error(f"Failed to update order status: {db_error}")
    
    finally:
        db.close()
        logger.info(f"Completed background processing for order ID: {order_id}")

async def process_high_priority_order(order_id: int):
    logger.info(f"Processing HIGH PRIORITY order ID: {order_id}")
    
    db = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"High priority order {order_id} not found")
            return
        
        order.status = OrderStatus.PROCESSING
        db.commit()
        logger.info(f"Processing HIGH PRIORITY order {order.order_id} - Status: {order.status.value}")
        
        priority_steps = [
            "Expedited order validation",
            "Priority inventory allocation",
            "Express shipping calculation", 
            "Immediate payment processing",
            "Priority shipping label generation",
            "Urgent customer notification",
            "Status update to processed"
        ]
        
        for i, step in enumerate(priority_steps, 1):
            logger.info(f"PRIORITY Step {i}: {step}")
            await asyncio.sleep(1)
        
        order.status = OrderStatus.PROCESSED
        db.commit()
        logger.info(f"HIGH PRIORITY order {order.order_id} - Status: {order.status.value}")
        
    except Exception as e:
        logger.error(f"Error processing high priority order {order_id}: {e}")
        if order:
            order.status = OrderStatus.FAILED
            db.commit()
    finally:
        db.close()
