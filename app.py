from flask import Flask, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a8c4f3d6e1b749f2a0c1d76f9e38e27a'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jeeva2005$'
app.config['MYSQL_DB'] = 'inventory'
mysql = MySQL(app)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        if existing_user:
            return "Username already exists"

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[1], password):  # Verify hashed password
            session['username'] = username
            return redirect(url_for('view_products'))
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = request.form['quantity']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (product_name, quantity) VALUES ( %s, %s)",
                    (product_name, quantity))
        
        cur.execute("INSERT INTO warehouse (prd_name, qty) VALUES (%s, %s)",
                    (product_name, quantity))
        mysql.connection.commit()


        mysql.connection.commit()

        cur.close()
        return redirect(url_for('view_products'))

    return render_template('add_product.html')


@app.route('/products')
def view_products():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return render_template('view_products.html', products=products)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = request.form['quantity']

        cur.execute("UPDATE products SET product_name = %s, quantity = %s WHERE product_id = %s",
                    (product_name, quantity, product_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_products'))

    cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()

    if product:
        return render_template('edit_product.html', product=product)
    else:
        return "Product not found."


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('view_products'))


@app.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        location_id = request.form['location_id']
        location_name = request.form['location_name']
        cur.execute("INSERT INTO locations (location_id, location_name) VALUES (%s, %s)",
                    (location_id, location_name))
        mysql.connection.commit()

    cur.execute("SELECT * FROM locations")
    locations = cur.fetchall()
    cur.close()
    return render_template('locations.html', locations=locations)


@app.route('/movements', methods=['GET', 'POST'])
def product_movements():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        qty = int(request.form['qty'])
        status = request.form['status']
        
        cur.execute("INSERT INTO product_movements (product_id, from_location, to_location, qty, status) VALUES (%s, %s, %s, %s, %s)",
                    (product_id, from_location, to_location, qty, status))
        mysql.connection.commit()

    cur.execute('''
        SELECT 
            p.product_name,
            f.location_name AS from_location,
            t.location_name AS to_location,
            pm.qty,
            pm.status,
            pm.timestamp
        FROM product_movements pm
        JOIN products p ON pm.product_id = p.product_id
        LEFT JOIN locations f ON pm.from_location = f.location_id
        LEFT JOIN locations t ON pm.to_location = t.location_id
        ORDER BY pm.timestamp DESC;
    ''')
    movements = cur.fetchall()

    cur.execute("SELECT product_id, product_name FROM products")
    products = cur.fetchall()

    cur.execute("SELECT location_id, location_name FROM locations")
    locations = cur.fetchall()

    cur.close()
    return render_template('movements.html', movements=movements, products=products, locations=locations)


@app.route('/product_locations')
def view_product_locations():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT p.product_name, 
            l.location_name, 
            SUM(CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END) - 
            SUM(CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END) AS qty
        FROM products p
        CROSS JOIN locations l
        LEFT JOIN product_movements pm ON pm.product_id = p.product_id
        GROUP BY p.product_name, l.location_name
        HAVING qty > 0
    ''')
    products_location_data = cur.fetchall()
    cur.close()

    return render_template('product_locations.html', products_location_data=products_location_data)


@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute('''
                SELECT  * FROM warehouse
                
                ''')
    warehouse_data = cur.fetchall()

    cur.execute(''' 
        SELECT p.product_name, COALESCE(l.location_name, 'N/A') AS warehouse, 
            SUM(CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END) - 
            SUM(CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END) AS qty
        FROM products p
        CROSS JOIN locations l
        LEFT JOIN product_movements pm ON pm.product_id = p.product_id
        GROUP BY p.product_name, l.location_name
        HAVING qty != 0
    ''')
    report_data = cur.fetchall()
    cur.close()

    return render_template('report.html', report_data=report_data , warehouse_data=warehouse_data)


@app.route('/in_transit')
def in_transit():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute(''' 
        SELECT 
            p.product_name,
            pm.qty,
            f.location_name AS from_warehouse,
            t.location_name AS to_warehouse,
            pm.timestamp
        FROM product_movements pm
        JOIN products p ON pm.product_id = p.product_id
        LEFT JOIN locations f ON pm.from_location = f.location_id
        LEFT JOIN locations t ON pm.to_location = t.location_id
        WHERE pm.status = 'Pending'
    ''')
    movements = cur.fetchall()
    cur.close()

    return render_template('in_transit.html', movements=movements)


@app.route('/product_history/<int:product_id>')
def product_history(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute(''' 
        SELECT 
            pm.timestamp,
            pm.qty,
            f.location_name AS from_location,
            t.location_name AS to_location,
            pm.status
        FROM product_movements pm
        LEFT JOIN locations f ON pm.from_location = f.location_id
        LEFT JOIN locations t ON pm.to_location = t.location_id
        WHERE pm.product_id = %s
        ORDER BY pm.timestamp DESC
    ''', (product_id,))
    movements = cur.fetchall()

    cur.execute("SELECT product_name FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()

    return render_template('product_history.html', product=product, movements=movements)


if __name__ == "__main__":
    app.run(debug=True)
