let cart = [];
let menuData = [];
let currentProduct = null;

document.addEventListener('DOMContentLoaded', () => {
    loadMenu();
});

async function loadMenu() {
    try {
        const res = await fetch('/products/api/menu');
        menuData = await res.json();
        renderCategories();
    } catch (e) {
        console.error("Error loading menu", e);
    }
}

function renderCategories() {
    const container = document.getElementById('categories-container');
    container.innerHTML = '';
    
    if (menuData.length > 0) {
        menuData.forEach((cat, index) => {
            const btn = document.createElement('button');
            btn.className = `category-btn ${index === 0 ? 'active' : ''}`;
            btn.innerText = cat.name;
            btn.onclick = () => {
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                renderProducts(cat.id);
            };
            container.appendChild(btn);
        });
        renderProducts(menuData[0].id);
    }
}

function renderProducts(categoryId) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';
    
    const category = menuData.find(c => c.id === categoryId);
    if (!category) return;
    
    category.products.forEach(p => {
        const div = document.createElement('div');
        div.className = 'product-card';
        div.innerHTML = `
            <h3>${p.name}</h3>
            <div class="price">$${p.price.toFixed(2)}</div>
        `;
        div.onclick = () => selectProduct(p);
        container.appendChild(div);
    });
}

function selectProduct(product) {
    currentProduct = product;
    document.getElementById('mod-product-name').innerText = product.name;
    document.querySelectorAll('.mod-input').forEach(cb => cb.checked = false);
    document.getElementById('modifiers-modal').classList.add('active');
}

function confirmProductAdd() {
    const modifiers = [];
    document.querySelectorAll('.mod-input:checked').forEach(cb => {
        modifiers.push({
            name: cb.value,
            extra_price: parseFloat(cb.dataset.price)
        });
    });
    
    cart.push({
        product_id: currentProduct.id,
        name: currentProduct.name,
        price: currentProduct.price,
        quantity: 1,
        modifiers: modifiers
    });
    
    currentProduct = null;
    closeModal('modifiers-modal');
    updateCartUI();
}

function updateCartUI() {
    const container = document.getElementById('cart-items');
    container.innerHTML = '';
    
    if (cart.length === 0) {
        container.innerHTML = '<div class="empty-cart text-muted text-center p-2 mt-3">La orden está vacía</div>';
        document.getElementById('cart-total').innerText = '$0.00';
        document.getElementById('btn-pay').disabled = true;
        document.getElementById('btn-send-kitchen').disabled = true;
        return;
    }
    
    let total = 0;
    cart.forEach((item, index) => {
        let itemSubtotal = item.price * item.quantity;
        let modsHtml = '';
        if (item.modifiers.length > 0) {
            modsHtml = '<div class="cart-item-mods">';
            item.modifiers.forEach(m => {
                itemSubtotal += m.extra_price * item.quantity;
                modsHtml += `+ ${m.name} ($${m.extra_price})<br>`;
            });
            modsHtml += '</div>';
        }
        total += itemSubtotal;
        
        container.innerHTML += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name px-1">${item.name}</div>
                    ${modsHtml}
                    <div class="qty-controls">
                        <button class="qty-btn" onclick="changeQty(${index}, -1)">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn" onclick="changeQty(${index}, 1)">+</button>
                    </div>
                </div>
                <div class="cart-item-price text-success fs-medium">$${itemSubtotal.toFixed(2)}</div>
            </div>
        `;
    });
    
    document.getElementById('cart-total').innerText = `$${total.toFixed(2)}`;
    document.getElementById('btn-pay').disabled = false;
    document.getElementById('btn-send-kitchen').disabled = false;
}

function changeQty(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    updateCartUI();
}

function clearCart() {
    if (confirm('¿Cancelar la orden actual?')) {
        cart = [];
        updateCartUI();
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

let currentOrderId = null;
let currentTotal = 0;

async function sendOrderToKitchen() {
    if (cart.length === 0) return;
    
    const payload = {
        order_type: document.getElementById('order-type').value,
        items: cart
    };
    
    try {
        const res = await fetch('/orders/api/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.success) {
            alert(`Orden #${data.order_id} enviada a cocina exitosamente.`);
            cart = [];
            updateCartUI();
        }
    } catch (e) {
        console.error("Error sending order", e);
        alert("Error al enviar orden.");
    }
}

async function openPaymentModal() {
    if (cart.length === 0) return;
    
    // First we send order to DB
    const payload = {
        order_type: document.getElementById('order-type').value,
        items: cart
    };
    
    try {
        const res = await fetch('/orders/api/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.success) {
            currentOrderId = data.order_id;
            currentTotal = data.total;
            
            document.getElementById('pay-total-display').innerText = `Total: $${currentTotal.toFixed(2)}`;
            document.getElementById('payment-amount').value = currentTotal.toFixed(2);
            document.getElementById('change-container').classList.add('hidden');
            
            document.getElementById('payment-modal').classList.add('active');
            calculateChange();
        }
    } catch (e) {
        console.error("Error creating order for payment", e);
        alert("Error al procesar la orden.");
    }
}

function calculateChange() {
    const received = parseFloat(document.getElementById('payment-amount').value) || 0;
    const change = received - currentTotal;
    
    if (change > 0) {
        document.getElementById('change-container').classList.remove('hidden');
        document.getElementById('change-display-value').innerText = `$${change.toFixed(2)}`;
    } else {
        document.getElementById('change-container').classList.add('hidden');
    }
}

async function processPayment() {
    const amount = parseFloat(document.getElementById('payment-amount').value) || 0;
    const method = document.getElementById('payment-method').value;
    
    if (amount < currentTotal && method === 'efectivo') {
        alert("El monto recibido es menor al total a pagar.");
        return;
    }
    
    const payload = {
        order_id: currentOrderId,
        payments: [{ method: method, amount: amount }]
    };
    
    try {
        const res = await fetch('/payments/api/pay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.success) {
            closeModal('payment-modal');
            document.getElementById('receipt-change').innerText = `Cambio ENTREGADO: $${data.change.toFixed(2)}`;
            document.getElementById('receipt-modal').classList.add('active');
        }
    } catch (e) {
        console.error("Error processing payment", e);
        alert("Error al procesar el pago.");
    }
}

function finishOrder() {
    cart = [];
    currentOrderId = null;
    currentTotal = 0;
    updateCartUI();
    closeModal('receipt-modal');
}

async function openPendingOrdersModal() {
    document.getElementById('pending-orders-modal').classList.add('active');
    const container = document.getElementById('pending-orders-list');
    container.innerHTML = '<div class="text-center p-3 text-muted">Cargando órdenes...</div>';
    
    try {
        const res = await fetch('/orders/api/pending');
        const orders = await res.json();
        
        if (orders.length === 0) {
            container.innerHTML = '<div class="text-center p-3 text-muted">No hay órdenes pendientes de cobro.</div>';
            return;
        }
        
        let html = '<div class="table-responsive"><table class="data-table"><thead><tr><th>ID</th><th>Tipo</th><th>Total</th><th>Estado</th><th>Acción</th></tr></thead><tbody>';
        orders.forEach(o => {
            html += `
                <tr>
                    <td>#${o.id}</td>
                    <td>${o.order_type}</td>
                    <td class="text-success font-weight-bold">$${o.total.toFixed(2)}</td>
                    <td>
                        <span class="badge ${o.status === 'lista' ? 'badge-primary' : 'badge-warning'}">${o.status}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="payPendingOrder(${o.id}, ${o.total})">Cobrar</button>
                    </td>
                </tr>
            `;
        });
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (e) {
        console.error("Error loading pending orders", e);
        container.innerHTML = '<div class="text-center p-3 text-danger">Error al cargar las órdenes.</div>';
    }
}

function payPendingOrder(orderId, total) {
    closeModal('pending-orders-modal');
    currentOrderId = orderId;
    currentTotal = total;
    
    document.getElementById('pay-total-display').innerText = `Total: $${currentTotal.toFixed(2)}`;
    document.getElementById('payment-amount').value = currentTotal.toFixed(2);
    document.getElementById('change-container').classList.add('hidden');
    
    document.getElementById('payment-modal').classList.add('active');
    calculateChange();
}
