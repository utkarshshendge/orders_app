from flask import Blueprint, request, jsonify
from app.orders.services import OrderService

orders_blueprint = Blueprint('orders', __name__)

@orders_blueprint.route('/', methods=['POST'])
def create_order():
    data = request.json
    try:
        order = OrderService.create_order(
            user_id=data['user_id'],
            order_id=data['order_id'],
            item_ids=data['item_ids'],
            total_amount=data['total_amount']
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Order craeted", "order_id": order.order_id}), 201

@orders_blueprint.route('/<order_id>', methods=['GET'])
def get_order_status(order_id):
    details = OrderService.get_order_status(order_id)
    if not details:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(details)

@orders_blueprint.route('/metrics', methods=['GET'])
def get_metrics():
    get_order_ids_param = request.args.get('getOrderIds', 'false').lower() == 'true'
    metrics = OrderService.get_metrics(get_order_ids=get_order_ids_param)
    return jsonify(metrics)


@orders_blueprint.route('/populate', methods=['POST'])
def populate_orders():
    data = request.json
    total_entries = data.get("total_entries")
    batch_id = data.get("batch_id")
    try:
        result = OrderService.populate_orders(total_entries, batch_id)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
