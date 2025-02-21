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


# API Documentation

## Overview
This API provides endpoints for managing orders, including creation, status retrieval, metrics tracking, and bulk order population.

## Base URL
- Base URL: `http://127.0.0.1:5000/orders`
- Note: Change base URL according to your local port configuration

## Endpoints

### 1. Create Order
- **Endpoint:** `/`
- **Method:** `POST`
- **Description:** Create a new order using the provided JSON payload

**Request Body:**
```json
{
  "user_id": 1,
  "order_id": "ORD003",
  "item_ids": [101, 102, 103],
  "total_amount": 59.99
}
```

**Example Request:**
```bash
curl --location 'http://127.0.0.1:5000/orders/' \
--header 'Content-Type: application/json' \
--data '{
  "user_id": 1,
  "order_id": "ORD003",
  "item_ids": [101, 102, 103],
  "total_amount": 59.99
}'
```

**Success Response (201):**
```json
{
    "message": "Order craeted",
    "order_id": "ORD003"
}
```

**Error Response (400):**
```json
{
    "error": "Error message details"
}
```

### 2. Get Order Status
- **Endpoint:** `/<order_id>`
- **Method:** `GET`
- **Description:** Retrieve status and details of a specific order

**Example Request:**
```bash
curl --location 'http://127.0.0.1:5000/orders/ORD003'
```

**Success Response (200):**
```json
{
    "completed_at": "2025-02-21T15:00:24.758685",
    "created_at": "2025-02-21T15:00:17",
    "item_ids": "101,102,103",
    "order_id": "ORD003",
    "pending_duration": 2.747467,
    "processing_duration": 5.011218,
    "processing_started_at": "2025-02-21T15:00:19.747467",
    "status": "Completed",
    "total_amount": 59.99,
    "total_duration": 7.758685,
    "user_id": 1
}
```

**Error Response (404):**
```json
{
    "error": "Order not found"
}
```

### 3. Get Order Metrics
- **Endpoint:** `/metrics`
- **Method:** `GET`
- **Description:** Retrieve metrics about orders including processing times and status counts
- **Query Parameters:** 
  - `getOrderIds`: (optional) Set to 'true' to include order IDs in the response

**Example Request:**
```bash
curl --location 'http://127.0.0.1:5000/orders/metrics?getOrderIds=true'
```

**Success Response (200):**
```json
{
    "average_processing_time": 5.011218,
    "average_processing_time_from_creation": 7.758685,
    "completed": {
        "count": 1,
        "order_ids": [
            "ORD003"
        ]
    },
    "pending": {
        "count": 0,
        "order_ids": []
    },
    "processing": {
        "count": 0,
        "order_ids": []
    },
    "total_orders": 1
}
```

### 4. Populate Orders (Bulk Creation)
- **Endpoint:** `/populate`
- **Method:** `POST`
- **Description:** Create multiple orders in bulk

**Request Body:**
```json
{
    "total_entries": 4,
    "batch_id": "optional-batch-identifier"
}
```

**Example Request:**
```bash
curl --location 'http://127.0.0.1:5000/orders/populate' \
--header 'Content-Type: application/json' \
--data '{
    "total_entries": 4
}'
```

**Success Response (201):**
```json
{
    "batch_id": "f3402fae",
    "errors": [],
    "failure_count": 0,
    "success_count": 4,
    "total_entries": 4
}
```

**Error Response (400):**
```json
{
    "error": "Error message details"
}
```

## Error Handling
- All endpoints return appropriate HTTP status codes
- Error responses include a JSON object with an "error" field containing the error message
- Common status codes:
  - 201: Successfully created
  - 200: Successful request
  - 400: Bad request
  - 404: Resource not found

## Notes
- All timestamps are returned in ISO 8601 format
- Duration values are in seconds
- Order IDs should be unique



