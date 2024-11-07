from flask_sqlalchemy import SQLAlchemy
from .extensions import db
from datetime import datetime

# User model to handle both regular users and admins
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user', lazy=True)  # Relationship to orders

# Category model for product categorization
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

# Product model for storing product details
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)  # Foreign key to Category
    image_url = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    sizes = db.Column(db.String, nullable=True)  # Field for storing multiple sizes


# Order model to track orders made by users
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(50), default='Pending')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

# OrderItem model to track individual products in an order
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(20), nullable=True) 
    product = db.relationship('Product')

