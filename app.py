from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "inventory_secret_key"

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            warehouse TEXT NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if count == 0:

        sample_products = [

            ("Laptop", 45, "WH-A"),
            ("Monitor", 30, "WH-A"),
            ("Keyboard", 5, "WH-B"),
            ("Mouse", 0, "WH-A"),
            ("Printer", 12, "WH-B"),
            ("Scanner", 4, "WH-B"),
            ("Router", 20, "WH-C"),
            ("SSD", 50, "WH-C"),
            ("UPS", 2, "WH-A"),
            ("Webcam", 18, "WH-B")

        ]

        conn.executemany(
            """
            INSERT INTO products
            (product_name, quantity, warehouse)
            VALUES (?, ?, ?)
            """,
            sample_products
        )

    conn.commit()
    conn.close()


# -----------------------------
# Login Page
# -----------------------------
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def handle_login():

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin123":
        session['username'] = username
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))


# -----------------------------
# Dashboard
# -----------------------------
@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    total_products = len(products)

    total_stock = sum(
        p['quantity']
        for p in products
    )

    available = sum(
        1 for p in products
        if p['quantity'] > 10
    )

    low_stock = sum(
        1 for p in products
        if 0 < p['quantity'] <= 10
    )

    out_of_stock = sum(
        1 for p in products
        if p['quantity'] == 0
    )

    return render_template(
        'dashboard.html',
        username=session['username'],
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        available=available,
        low_stock=low_stock,
        out_of_stock=out_of_stock
    )


# -----------------------------
# Product Management
# -----------------------------
@app.route('/products')
def products():

    conn = get_db_connection()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        'products.html',
        products=products
    )

@app.route('/add_product', methods=['POST'])
def add_product():

    product_name = request.form['product_name']
    quantity = request.form['quantity']
    warehouse = request.form['warehouse']

    conn = get_db_connection()

    conn.execute(
        '''
        INSERT INTO products
        (product_name, quantity, warehouse)
        VALUES (?, ?, ?)
        ''',
        (product_name, quantity, warehouse)
    )

    conn.commit()
    conn.close()

    return redirect('/products')
@app.route('/delete_product/<int:id>')
def delete_product(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/products')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    conn = get_db_connection()

    if request.method == 'POST':

        product_name = request.form['product_name']
        quantity = request.form['quantity']
        warehouse = request.form['warehouse']

        conn.execute(
            '''
            UPDATE products
            SET product_name=?,
                quantity=?,
                warehouse=?
            WHERE id=?
            ''',
            (product_name, quantity, warehouse, id)
        )

        conn.commit()
        conn.close()

        return redirect('/products')

    product = conn.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'edit_product.html',
        product=product
    )

# -----------------------------
# Inventory Tracking
# -----------------------------
@app.route('/inventory')
def inventory():

    conn = get_db_connection()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        'inventory.html',
        products=products
    )


# -----------------------------
# Alerts
# -----------------------------
@app.route('/alerts')
def alerts():

    conn = get_db_connection()

    alerts_products = conn.execute("""
        SELECT *
        FROM products
        WHERE quantity <= 10
    """).fetchall()

    conn.close()

    return render_template(
        'alerts.html',
        products=alerts_products
    )


# -----------------------------
# Logout
# -----------------------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)