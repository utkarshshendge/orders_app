import threading
from concurrent.futures import ThreadPoolExecutor
from app.orders.services import OrderService, order_queue

def process_order_taask(app, order_id):
    with app.app_context():
        print(f"Processing order n: {order_id}")
        OrderService.process_order(order_id)
        order_queue.task_done()

def worker(app, executor):
    while True:
        # block until an order is available.
        order_id = order_queue.get(block=True)
        # process the order concurrently.
        executor.submit(process_order_taask, app, order_id)

def start_worker(app, max_workers=100):

   # Adjust max_workers based on load and available resourses.

    executor = ThreadPoolExecutor(max_workers=max_workers)
    thread = threading.Thread(target=worker, args=(app, executor), daemon=True)
    thread.start()
