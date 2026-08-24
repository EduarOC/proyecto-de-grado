
let cartTotal = 0;
let cartItems = [];

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
                                <button class="add-btn" onclick="addToCart(${dish.price}, '${dish.name}')">Añadir</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        });
});

function addToCart(price, name) {
    cartTotal += price;
    cartItems.push(name);
    const cartBar = document.getElementById('cart-bar');
    cartBar.style.display = 'flex';
    document.getElementById('cart-total').innerText = 'Total: $' + cartTotal.toLocaleString();
}

function payOrder(mesa) {
    if(cartTotal === 0) return;
    
    // Cuenta cuántos de cada plato hay para enviar a la cocina
    const itemCount = {};
    cartItems.forEach(item => { itemCount[item] = (itemCount[item] || 0) + 1; });
    const itemsString = Object.entries(itemCount).map(([name, count]) => `${count}x ${name}`).join(', ');

    fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ total: cartTotal, table: mesa, items: itemsString })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            alert('✅ ¡Pago verificado por Pasarela! Tu pedido ha sido enviado a la cocina.');
            cartTotal = 0;
            cartItems = [];
            document.getElementById('cart-bar').style.display = 'none';
        }
    });
}
