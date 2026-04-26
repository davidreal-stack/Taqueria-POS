from flask import Blueprint, render_template, session, redirect, url_for
from models import Order, Payment
from database import db
from sqlalchemy import func
from datetime import datetime, date

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin': return redirect(url_for('auth.login'))
    
    today = date.today()
    # Basic stats for MVP
    orders_today = Order.query.all() # In SQLite dates can be tricky with SQLAlchemy, so we can filter in python for MVP if needed, or query.filter(func.date(Order.created_at) == today).
    
    # Simple Python filtering for robust SQLite support without complex datetime functions
    orders_today = [o for o in orders_today if o.created_at.date() == today]
    
    total_sales = sum(o.total for o in orders_today if o.status == 'completada')
    completed_orders = [o for o in orders_today if o.status == 'completada']
    
    return render_template('dashboard.html', total_sales=total_sales, order_count=len(completed_orders), recent_orders=orders_today[-10:])

@reports_bp.route('/')
def index():
    if session.get('role') != 'admin': return redirect(url_for('auth.login'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template('reports.html', orders=orders)
