import time
import pytest
from app import create_app, db
from app.orders.models import Order, OrderStatus
from app.orders.services import OrderService, order_queue

# Fixtures 

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test API Endpoints 

def test_create_order(client, app):
    data = {
        "user_id": 1,
        "order_id": "ORD_TEST_1",
        "item_ids": [101, 102],
        "total_amount": 50.75
    }

    response = client.post('/orders/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["order_id"] == "ORD_TEST_1"
    
    with app.app_context():
        order = Order.query.filter_by(order_id="ORD_TEST_1").first()
        assert order is not None
        assert order.total_amount == 50.75

def test_get_order_status(client, app):
    with app.app_context():
        OrderService.create_order(
            user_id=2, order_id="ORD_TEST_2", item_ids=[201, 202], total_amount=100.0
        )
    response = client.get('/orders/ORD_TEST_2')
    assert response.status_code == 200
    resp_json = response.get_json()
    assert resp_json["order_id"] == "ORD_TEST_2"
    assert resp_json["status"] == OrderStatus.PENDING.value

def test_populate_orders(client, app):
    data = {"total_entries": 10, "batch_id": "TESTBATCH"}
    response = client.post('/orders/populate', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["batch_id"] == "TESTBATCH"
    assert resp_json["total_entries"] == 10
    assert resp_json["success_count"] == 10

def test_get_metrics_without_order_ids(client, app):
    with app.app_context():
        order = OrderService.create_order(
            user_id=3, order_id="ORD_METRIC_1", item_ids=[301], total_amount=20.0
        )
        order.status = OrderStatus.COMPLETED
        order.processing_started_at = order.created_at
        order.completed_at = order.created_at
        db.session.commit()
    response = client.get('/orders/metrics?getOrderIds=false')
    resp_json = response.get_json()
    assert "pending" in resp_json
    assert resp_json["pending"]["order_ids"] == []

def test_get_metrics_with_order_ids(client, app):
    with app.app_context():
        order = OrderService.create_order(
            user_id=3, order_id="ORD_METRIC_2", item_ids=[302], total_amount=30.0
        )
        order.status = OrderStatus.COMPLETED
        order.processing_started_at = order.created_at
        order.completed_at = order.created_at
        db.session.commit()
    response = client.get('/orders/metrics?getOrderIds=true')
    resp_json = response.get_json()
    assert "completed" in resp_json
    assert resp_json["completed"]["order_ids"] == ["ORD_METRIC_2"]



# Test Queue

def test_queue_processing(app):
    """
    Create an order that is added to the queue. Then wait long enough
    for the worker (which processes orders asynchronously) to process it.
    """
    with app.app_context():
        OrderService.create_order(
            user_id=4, order_id="ORD_QUEUE_1", item_ids=[401], total_amount=30.0
        )

    time.sleep(10)
    with app.app_context():
        processed_order = Order.query.filter_by(order_id="ORD_QUEUE_1").first()
        assert processed_order.status == OrderStatus.COMPLETED
