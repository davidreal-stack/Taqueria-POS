from flask import Blueprint, request, jsonify, session
from models import Order, Payment
from database import db

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/api/pay', methods=['POST'])
def process_payment():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    order_id = data.get('order_id')
    payments = data.get('payments', []) # Ex: [{'method': 'efectivo', 'amount': 100}, {'method': 'tarjeta', 'amount': 50}]
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
        
    total_paid = sum(float(p.get('amount', 0)) for p in payments)
    
    for p in payments:
        amount = float(p.get('amount', 0))
        if amount > 0:
            payment = Payment(
                order_id=order.id,
                method=p.get('method'),
                amount=amount
            )
            db.session.add(payment)
            
    if total_paid >= order.total:
        order.status = 'completada'
        
    db.session.commit()
    return jsonify({'success': True, 'order_status': order.status, 'change': max(0, total_paid - order.total)})
