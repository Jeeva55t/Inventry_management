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

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
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
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username  # Store login state
            return redirect(url_for('add_product'))  # Redirect to add_product page
        else:
            return "Invalid credentials"

    return render_template('login.html')

# ------------------ Logout -------------------


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
       

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (product_id, product_name) VALUES (%s, %s)", 
                    (product_id, product_name))
        mysql.connection.commit()
        cur.close()
        return "Product added successfully!"

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


@app.route('/update/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
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
        return render_template('update_product.html', product=product)
    else:
        return "Product not found."

# ------------------ Delete Product -------------------
@app.route('/delete/<product_id>', methods=['GET'])
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('view_products'))

if __name__ == "__main__":
    app.run(debug=True)
