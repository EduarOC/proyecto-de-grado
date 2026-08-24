
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import sqlite3
import qrcode
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = "super_secreto_para_sesiones"
DB_PATH = 'restaurant.db'

# Imágenes reales de Unsplash para darle el toque profesional
IMG_HAMBURGUESA = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80"
IMG_PIZZA = "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&q=80"
IMG_JUGO = "https://images.unsplash.com/photo-1600271886742-f049cd451b51?w=400&q=80"
IMG_POSTRE = "https://images.unsplash.com/photo-1551024506-0cb4a1cb2983?w=400&q=80"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabla de Usuarios (Staff)
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    # Tabla de Platos
    c.execute('''CREATE TABLE IF NOT EXISTS dishes (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, price REAL, image TEXT)''')
    # Tabla de Pedidos
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, table_num INTEGER, total REAL, status TEXT, items TEXT)''')
    
    # Insertar Usuarios de prueba
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES ('admin', '1234', 'admin')")
        c.execute("INSERT INTO users (username, password, role) VALUES ('chef', '1234', 'chef')")
        c.execute("INSERT INTO users (username, password, role) VALUES ('mesero', '1234', 'mesero')")
        
    # Insertar Platos con imágenes reales
    c.execute("SELECT COUNT(*) FROM dishes")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO dishes (name, desc, price, image) VALUES ('Hamburguesa Clásica', 'Carne 100% res, queso cheddar fundido, vegetales frescos y papas rústicas.', 28000, ?)", (IMG_HAMBURGUESA,))
        c.execute("INSERT INTO dishes (name, desc, price, image) VALUES ('Pizza Artesanal', 'Masa madre, salsa pomodoro, mozzarella y albahaca.', 32000, ?)", (IMG_PIZZA,))
        c.execute("INSERT INTO dishes (name, desc, price, image) VALUES ('Jugo Natural', 'Refrescante bebida de mango o fresa sin azúcar.', 8000, ?)", (IMG_JUGO,))
        c.execute("INSERT INTO dishes (name, desc, price, image) VALUES ('Postre de Natas', 'Receta tradicional colombiana con caramelo.', 12000, ?)", (IMG_POSTRE,))
        
    conn.commit()
    conn.close()

# ----- RUTAS PUBLICAS (CLIENTES) -----
@app.route('/')
def home():
    # Si alguien entra a la raíz, le pedimos que escanee un QR de una mesa
    return "Por favor escanea el Código QR de tu mesa para hacer el pedido."

@app.route('/mesa/<int:num>')
def menu_mesa(num):
    # Vista interactiva del comensal
    return render_template('index.html', mesa=num)

@app.route('/qr/<int:num>')
def generate_qr(num):
    # Genera una imagen QR dinámicamente apuntando a la mesa
    url = request.host_url + f"mesa/{num}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# ----- RUTAS DE AUTENTICACION -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (user, pw))
        row = c.fetchone()
        conn.close()
        
        if row:
            session['role'] = row[0]
            if row[0] == 'admin': return redirect(url_for('admin'))
            if row[0] == 'chef': return redirect(url_for('chef'))
            if row[0] == 'mesero': return redirect(url_for('mesero'))
        else:
            return "Credenciales inválidas. Intenta 'admin', 'chef' o 'mesero' con clave '1234'."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----- RUTAS PRIVADAS (STAFF) -----
@app.route('/admin')
def admin():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/chef')
def chef():
    if session.get('role') != 'chef': return redirect(url_for('login'))
    return render_template('chef.html')

@app.route('/mesero')
def mesero():
    if session.get('role') != 'mesero': return redirect(url_for('login'))
    return render_template('mesero.html')

# ----- API ENDPOINTS -----
@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM dishes")
    items = [{"id": row[0], "name": row[1], "desc": row[2], "price": row[3], "image": row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    total = data.get('total', 0)
    table = data.get('table', 1)
    items_str = data.get('items', 'Varios platos')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO orders (table_num, total, status, items) VALUES (?, ?, 'En Cocina', ?)", (table, total, items_str))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    # Permite filtrar pedidos por estado (ej. para que el chef solo vea los 'En Cocina')
    status_filter = request.args.get('status')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if status_filter:
        c.execute("SELECT * FROM orders WHERE status=? ORDER BY id ASC", (status_filter,))
    else:
        c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = [{"id": row[0], "table": row[1], "total": row[2], "status": row[3], "items": row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(orders)

@app.route('/api/update_order', methods=['POST'])
def update_order():
    data = request.json
    order_id = data.get('id')
    new_status = data.get('status')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    init_db()
    # host=0.0.0.0 y PORT por variable de entorno: necesario para desplegar en un
    # ambiente DEV/UAT real (Render, etc.), no solo en localhost.
    #
    # IMPORTANTE DE SEGURIDAD: el modo debug de Flask NUNCA debe quedar activo en un
    # servidor accesible públicamente (el debugger de Werkzeug permite ejecución remota
    # de código si alguien lo alcanza). Por defecto queda apagado; solo se activa si se
    # define explícitamente FLASK_DEBUG=1 para desarrollo local.
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
