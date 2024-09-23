from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from .extensions import db, migrate
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    # Import and register your blueprints (routes)
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .product_routes import product_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(product_bp)

    return app
