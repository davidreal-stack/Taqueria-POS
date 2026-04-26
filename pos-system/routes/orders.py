import json
from flask import Blueprint, render_template, request, session, jsonify, url_for, redirect
from models import Order, OrderItem, Product, Category
from database import db

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/pos', methods=['GET'])
def pos():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('pos.html')

@orders_bp.route('/api/create', methods=['POST'])
def create_order():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    order_type = data.get('order_type', 'Mesa 1')
    items = data.get('items', [])
    
    new_order = Order(
        user_id=session['user_id'],
        order_type=order_type,
        status='pendiente',
        total=0.0
    )
    db.session.add(new_order)
    db.session.flush() # get new_order.id
    
    total = 0.0
    for item in items:
        product = Product.query.get(item['product_id'])
        if product:
            quantity = item.get('quantity', 1)
            subtotal = product.price * quantity
            
            # Modifiers processing
            modifiers = item.get('modifiers', [])
            for mod in modifiers:
                subtotal += mod.get('extra_price', 0) * quantity
                
            total += subtotal
            
            # Determine initial status by area
            area = product.category.area if product.category else 'caja'
            status = 'listo' if area == 'caja' else 'pendiente'
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                modifiers_snapshot=json.dumps(modifiers),
                subtotal=subtotal,
                status=status
            )
            
            db.session.add(order_item)
            
    new_order.total = total
    db.session.commit()
    
    return jsonify({'success': True, 'order_id': new_order.id, 'total': total})

@orders_bp.route('/api/pending', methods=['GET'])
def get_pending_orders():
    orders = Order.query.filter(Order.status != 'completada').order_by(Order.created_at.desc()).all()
    data = []
    for o in orders:
        data.append({
            'id': o.id,
            'order_type': o.order_type,
            'status': o.status,
            'total': o.total,
            'created_at': o.created_at.strftime('%H:%M:%S')
        })
    return jsonify(data)

@orders_bp.route('/kitchen/<area>', methods=['GET'])
def kitchen_view(area):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('kitchen.html', area=area)

@orders_bp.route('/api/kitchen/<area>', methods=['GET'])
def api_kitchen_orders(area):
    items = OrderItem.query.filter_by(status='pendiente').join(Product).join(Category).filter(Category.area == area).all()
    
    orders_dict = {}
    for item in items:
        order = item.order
        if order.id not in orders_dict:
            orders_dict[order.id] = {
                'id': order.id,
                'order_type': order.order_type,
                'created_at': order.created_at.strftime('%H:%M:%S'),
                'items': []
            }
        
        orders_dict[order.id]['items'].append({
            'item_id': item.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'modifiers': item.get_modifiers()
        })
        
    return jsonify(list(orders_dict.values()))

@orders_bp.route('/api/kitchen/item/<int:item_id>/ready', methods=['POST'])
def mark_item_ready(item_id):
    item = OrderItem.query.get(item_id)
    if item:
        item.status = 'listo'
        db.session.commit()
        
        # Check if all items in order are ready
        order = item.order
        all_ready = all(i.status == 'listo' for i in order.items)
        if all_ready and order.status != 'completada':
            order.status = 'lista'
            db.session.commit()
            
        return jsonify({'success': True, 'order_ready': all_ready})
    return jsonify({'error': 'Not found'}), 404
