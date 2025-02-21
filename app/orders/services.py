from app.extensions import db
from app.orders.models import Order, OrderStatus
from datetime import datetime
import queue
import time
import random
import uuid

# in-memory queue as requiured in the assignment
order_queue = queue.Queue()

class OrderService:
    @staticmethod
    def create_order(user_id, order_id, item_ids, total_amount):
        # check for duplicate order_id
        if Order.query.filter_by(order_id=order_id).first():
            raise ValueError("Order with this order_id already exists.")
            
        new_order = Order(
            user_id=user_id,
            order_id=order_id,
            item_ids=",".join(map(str, item_ids)),
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        db.session.add(new_order)
        db.session.commit()
        order_queue.put(new_order.id)
        return new_order
    


    @staticmethod
    def get_order_status(order_id):
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return None
        details = {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "item_ids": order.item_ids,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "processing_started_at": order.processing_started_at.isoformat() if order.processing_started_at else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        }
        if order.processing_started_at:
            details["pending_duration"] = (order.processing_started_at - order.created_at).total_seconds()
        if order.completed_at and order.processing_started_at:
            details["processing_duration"] = (order.completed_at - order.processing_started_at).total_seconds()
            details["total_duration"] = (order.completed_at - order.created_at).total_seconds()
        return details
    

    @staticmethod
    def get_metrics(get_order_ids=False):
        try:
            total_orders = Order.query.count()
            
            # Always fetch completed orders because we need them for average calculetions.
            completed_orders = Order.query.filter_by(status=OrderStatus.COMPLETED).all()
            
            if get_order_ids:
                pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).all()
                processing_orders = Order.query.filter_by(status=OrderStatus.PROCESSING).all()
                
                pending = {
                    "count": len(pending_orders),
                    "order_ids": [o.order_id for o in pending_orders]
                }
                processing = {
                    "count": len(processing_orders),
                    "order_ids": [o.order_id for o in processing_orders]
                }
                completed = {
                    "count": len(completed_orders),
                    "order_ids": [o.order_id for o in completed_orders]
                }
            else:
                pending_count = Order.query.filter_by(status=OrderStatus.PENDING).count()
                processing_count = Order.query.filter_by(status=OrderStatus.PROCESSING).count()
                
                pending = {"count": pending_count, "order_ids": []}
                processing = {"count": processing_count, "order_ids": []}
                completed = {"count": len(completed_orders), "order_ids": []}
            
            if completed_orders:
                avg_processing_time = sum(
                    [(o.completed_at - o.processing_started_at).total_seconds()
                    for o in completed_orders if o.processing_started_at and o.completed_at]
                ) / len(completed_orders)
                
                avg_processing_time_from_creation = sum(
                    [(o.completed_at - o.created_at).total_seconds()
                    for o in completed_orders if o.created_at and o.completed_at]
                ) / len(completed_orders)
            else:
                avg_processing_time = 0
                avg_processing_time_from_creation = 0

            metrics = {
                "total_orders": total_orders,
                "average_processing_time": avg_processing_time,
                "average_processing_time_from_creation": avg_processing_time_from_creation,
                "pending": pending,
                "processing": processing,
                "completed": completed,
            }
            
            print("Metrics computed:", metrics)
            return metrics
        except Exception as e:
            print("Error in get_metrics:", e)
            return {}


    @staticmethod
    def process_order(order_id):
        order = Order.query.get(order_id)
        if not order:
            return

         # Simulate  delay
        time.sleep(2)
        
        order.status = OrderStatus.PROCESSING
        order.processing_started_at = datetime.utcnow()
        db.session.commit()

        # Simulate random delay in processing state (3-7 seconds)
        delay_processing = random.randint(3, 7)
        time.sleep(delay_processing)
        
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def populate_orders(total_entries, batch_id=None):
        """
        populates multiple orders at once. Each order_id is generated using a batch id.
        If a batch_id is provided and orders with that prefix exist, it raises error.
        """
        if not isinstance(total_entries, int) or total_entries <= 0:
            raise ValueError("Invalid total_entries value. Must be a positive integer.")

        if not batch_id:
            batch_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID

        # prevent duplicate batch 
        existing = Order.query.filter(Order.order_id.like(f"sim_{batch_id}_%")).first()
        if existing:
            raise ValueError(f"Orders for batch_id '{batch_id}' already exist. Please use a unique batch_id.")

        success_count = 0
        failure_count = 0
        errors = []

        for i in range(1, total_entries + 1):
            order_id = f"sim_{batch_id}_{i}"
            # Generate a random list of item_ids with length between 1 and 3.
            length = random.randint(1, 3)
            item_ids = [random.randint(1, 100) for _ in range(length)]
            # Generate a random total_amount between 10 and 100 with 2 deci places.
            total_amount = round(random.uniform(10, 100), 2)
            try:
                # Use user_id=0 for simulated orders.
                OrderService.create_order(user_id=0, order_id=order_id, item_ids=item_ids, total_amount=total_amount)
                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"{order_id}: {str(e)}")
        
        return {
            "batch_id": batch_id,
            "total_entries": total_entries,
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": errors
        }
