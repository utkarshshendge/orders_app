from flask import Flask
from app.extensions import db
from app.config import Config
from app.orders.routes import orders_blueprint
from app.worker import start_worker
from sqlalchemy import text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    with app.app_context():
        db.session.execute(text("PRAGMA journal_mode=WAL;"))
        db.create_all()

    # Register blueprints for feature-based modules
    app.register_blueprint(orders_blueprint, url_prefix='/orders')
    # app.register_blueprint(users_blueprint, url_prefix='/users')  # for future use, when we want to perform operations on user model

    start_worker(app)

    return app
