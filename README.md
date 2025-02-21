# Order Processing Backend in FLASK

This project is a backend system for managing and processing orders in an e-commerce platform. It provides a RESTful API for order creation, status checking, metrics reporting, and load simulation using an in-memory queue with asynchronous processing. The design is modular, adheres to SOLID principles, and is structured for easy extension (for example, adding a user management module in the future).

## Features

- **Order Creation:** Create orders with fields such as `user_id`, `order_id`, `item_ids`, and `total_amount`.
- **Asynchronous Processing:** Orders are processed asynchronously via an in-memory queue using a `ThreadPoolExecutor`.
- **Order Status:** Check order status (Pending, Processing, Completed) along with detailed timing information.
- **Metrics:** Retrieve key metrics including total orders, average processing time (from processing start and from creation), and counts (plus optionally, lists) of orders by status.
- **Load Simulation:** A `/orders/populate` endpoint to simulate load by creating many orders at once.
- **Modular Design:** Structured by feature (e.g., orders, users) to facilitate future expansion.

##  Setting things up

- Create a virtual env: `python -m venv venv`
- Activate venv `source venv/bin/activate`
- Install requirements.txt `pip install -r requirements.txt`
- Note: I am using `Python 3.13.1`


##  Running the flask app
- Run `python3 run.py`
- To run tests use the command : `pytest tests/test_orders.py  `

