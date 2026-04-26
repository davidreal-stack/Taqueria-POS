from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='cajero') # admin, cajero, cocina
    
    orders = db.relationship('Order', backref='cashier', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    area = db.Column(db.String(64), nullable=False) # parrilla, tacos, caja
    
    products = db.relationship('Product', backref='category', lazy='dynamic')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    modifiers = db.relationship('Modifier', backref='product', lazy='dynamic')


class Modifier(db.Model):
    __tablename__ = 'modifiers'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True) # If null, applies to all or category
    name = db.Column(db.String(64), nullable=False)
    extra_price = db.Column(db.Float, default=0.0)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_type = db.Column(db.String(20), nullable=False) # Mesa X, Para llevar, Domicilio
    status = db.Column(db.String(20), default='pendiente') # pendiente, en preparacion, lista, completada
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    payments = db.relationship('Payment', backref='order', lazy='dynamic')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    modifiers_snapshot = db.Column(db.Text, nullable=True) # JSON string of chosen modifiers
    subtotal = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pendiente') # pendiente, listo
    
    product = db.relationship('Product')

    def get_modifiers(self):
        if self.modifiers_snapshot:
            return json.loads(self.modifiers_snapshot)
        return []


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    method = db.Column(db.String(20), nullable=False) # efectivo, tarjeta, transferencia
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
