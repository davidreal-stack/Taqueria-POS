from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import Product, Category, Modifier
from database import db

products_bp = Blueprint('products', __name__, url_prefix='/products')

def admin_required():
    return session.get('role') == 'admin'

@products_bp.route('/', methods=['GET'])
def list_products():
    if not admin_required(): return redirect(url_for('auth.login'))
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories)

@products_bp.route('/api/menu', methods=['GET'])
def api_menu():
    categories = Category.query.all()
    data = []
    for c in categories:
        products = Product.query.filter_by(category_id=c.id, active=True).all()
        data.append({
            'id': c.id,
            'name': c.name,
            'products': [{'id': p.id, 'name': p.name, 'price': p.price} for p in products]
        })
    return jsonify(data)
