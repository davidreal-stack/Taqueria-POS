import os
from flask import Flask, redirect, url_for
from config import Config
from database import db
from models import User, Category, Product

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.payments import payments_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(reports_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        seed_data()
        
    return app

def seed_data():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        
        # Initial Categories
        c1 = Category(name='Tacos', area='tacos')
        c2 = Category(name='Hamburguesas', area='parrilla')
        c3 = Category(name='Bebidas', area='caja')
        db.session.add_all([c1, c2, c3])
        db.session.commit()
        
        # Initial Products
        db.session.add_all([
            Product(category_id=c1.id, name='Taco de Bistec', price=30.0),
            Product(category_id=c1.id, name='Taco de Pastor', price=25.0),
            Product(category_id=c1.id, name='Orden Pastor', price=80.0),
            Product(category_id=c2.id, name='Hamburguesa Sencilla', price=80.0),
            Product(category_id=c2.id, name='Hamburguesa Especial', price=120.0),
            Product(category_id=c3.id, name='Refresco', price=25.0),
            Product(category_id=c3.id, name='Agua Fresca', price=20.0),
        ])
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
