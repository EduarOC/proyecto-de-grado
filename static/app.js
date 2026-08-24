
// El carrito guarda { [dishId]: { name, price, qty } }. El precio mostrado aquí es solo
// para la experiencia del usuario: el total real siempre se recalcula en el servidor
// a partir de la tabla `dishes` (ver /api/order en app.py) para que nadie pueda manipular
// precios o cantidades negativas desde el navegador.
let cart = {};

document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/dishes')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('menu-container');
            data.forEach(dish => {
                container.innerHTML += `
                    <div class="dish-card">
                        <img class="dish-image" src="${dish.image}" alt="${dish.name}">
                        <div class="dish-content">
                            <div class="dish-info">
                                <h3>${dish.name}</h3>
                                <p>${dish.desc}</p>
                            </div>
                            <div class="dish-bottom">
                                <span class="dish-price">$${dish.price.toLocaleString()} COP</span>
                                <button class="add-btn" onclick="addToCart(${dish.id}, ${dish.price}, '${dish.name}')">Añadir</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        });
});

function addToCart(id, price, name) {
    if (!cart[id]) {
        cart[id] = { name, price, qty: 0 };
    }
    cart[id].qty += 1;
    updateCartBar();
}

function updateCartBar() {
    const cartBar = document.getElementById('cart-bar');
    const entries = Object.values(cart);
    if (entries.length === 0) {
        cartBar.style.display = 'none';
        return;
    }
    // Este total es solo informativo para el cliente; el servidor lo vuelve a calcular.
    const total = entries.reduce((sum, item) => sum + item.price * item.qty, 0);
    cartBar.style.display = 'flex';
    document.getElementById('cart-total').innerText = 'Total: $' + total.toLocaleString();
}

function payOrder(mesa) {
    const items = Object.entries(cart).map(([id, item]) => ({ id: parseInt(id, 10), qty: item.qty }));
    if (items.length === 0) return;

    fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table: mesa, items })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('✅ ¡Pago verificado por Pasarela! Tu pedido ha sido enviado a la cocina.');
            cart = {};
            updateCartBar();
        } else {
            alert('⚠️ ' + (data.error || 'No se pudo procesar el pedido.'));
        }
    });
}
