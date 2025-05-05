from flask import Flask, render_template, request, redirect, url_for, session, flash
import MySQLdb
from datetime import datetime

app = Flask(__name__)
app.secret_key = "a8c4f3d6e1b749f2a0c1d76f9e38e27a"

db = MySQLdb.connect(host="localhost", user="root", passwd="jeeva2005$", db="inventory")
cur = db.cursor()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['product_name']
        quantity = int(request.form['quantity'])
        cur.execute("INSERT INTO products (name) VALUES (%s)", (name,))
        db.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        product_id = cur.fetchone()[0]
        # First, get the id of the warehouse
        cur.execute("SELECT id FROM locations WHERE name = %s", ('warehouse',))
        location_id = cur.fetchone()[0]

        # Then insert into inventory
        cur.execute("INSERT INTO inventory (product_id, location_id, quantity) VALUES (%s, %s, %s)", (product_id, location_id, quantity))
        db.commit()
        flash('Product added to warehouse')
        return redirect(url_for('home'))
    return render_template('add_product.html')

@app.route('/move', methods=['GET', 'POST'])
def move_products():
    cur = db.cursor()  # ✅ Make sure this is here at the top of the function
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        quantity = int(request.form['quantity'])

        # Check if enough stock is available at from_location
        cur.execute("SELECT quantity FROM inventory WHERE product_id=%s AND location_id=%s", (product_id, from_location))
        result = cur.fetchone()
        if not result or result[0] < quantity:
            flash("Not enough stock at source location")
            return redirect(url_for('move_products'))

        # Deduct from source
        cur.execute("""
            UPDATE inventory SET quantity = quantity - %s
            WHERE product_id = %s AND location_id = %s
        """, (quantity, product_id, from_location))

        # Add to destination (insert if not exists)
        cur.execute("""
            INSERT INTO inventory (product_id, location_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (product_id, to_location, quantity, quantity))

        # Log movement (optional)
        cur.execute("""
            INSERT INTO movements (product_id, from_location_id, to_location_id, quantity)
            VALUES (%s, %s, %s, %s)
        """, (product_id, from_location, to_location, quantity))

        db.commit()
        flash("Product moved successfully")
        return redirect(url_for('home'))

    # Fetch locations and products for the form
    cur.execute("SELECT id, name FROM locations")
    locations = cur.fetchall()
    cur.execute("SELECT id, name FROM products")
    products = cur.fetchall()

    return render_template("move_products.html", products=products, locations=locations)


@app.route('/report')
def report():
    cur = db.cursor()
    cur.execute("""
        SELECT p.name AS product_name, l.name AS location_name, i.quantity
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN locations l ON i.location_id = l.id
    """)
    data = cur.fetchall()
    return render_template('report.html', data=data)


@app.route('/intransit')
def intransit():
    cur.execute("""
        SELECT m.product_id, p.product_name, m.from_location_id, m.to_location_id, m.quantity, m.timestamp
        FROM movements m
        JOIN products p ON m.product_id = p.id
        ORDER BY m.timestamp DESC
    """)
    movements = cur.fetchall()
    return render_template('in_transit.html', movements=movements)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location = request.form['location_name']
        cur.execute("INSERT INTO locations (location_name) VALUES (%s)", (location,))
        db.commit()
        flash('Location added')
        return redirect(url_for('home'))
    return render_template('add_location.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
