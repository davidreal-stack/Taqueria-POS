from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User
from database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            
            if user.role == 'admin':
                return redirect(url_for('reports.dashboard'))
            elif user.role == 'cocina':
                return redirect(url_for('orders.kitchen_view', area='parrilla'))
            else:
                return redirect(url_for('orders.pos'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
