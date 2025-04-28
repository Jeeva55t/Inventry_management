from flask import Flask, request, render_template_string, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jeeva2005$'
app.config['MYSQL_DB'] = 'inventory_db'

mysql = MySQL(app)

# Home Page - Add Product
@app.route('/', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        quantity = request.form['quantity']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (product_id, product_name, quantity) VALUES (%s, %s, %s)", 
                    (product_id, product_name, quantity))
        mysql.connection.commit()
        cur.close()
        return "Product added successfully!"
    
    return '''
    <h2>Add Product</h2>
    <form method="POST">
        Product ID: <input type="text" name="product_id"><br><br>
        Product Name: <input type="text" name="product_name"><br><br>
        Quantity: <input type="number" name="quantity"><br><br>
        <input type="submit" value="Add Product">
    </form>
    '''

# View all products
@app.route('/products')
def view_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    html = '''
    <h2>Products</h2>
    <table border="1">
        <tr><th>Product ID</th><th>Product Name</th><th>Quantity</th><th>Action</th></tr>
        {% for p in products %}
            <tr>
                <td>{{ p[0] }}</td>
                <td>{{ p[1] }}</td>
                <td>{{ p[2] }}</td>
                <td><a href="{{ url_for('update_product', product_id=p[0]) }}">Edit</a></td>
            </tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, products=products)

# Update a product
@app.route('/update/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = request.form['quantity']

        cur.execute("UPDATE products SET product_name = %s, quantity = %s WHERE product_id = %s",
                    (product_name, quantity, product_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_products'))

    # GET request — show current data
    cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()

    if product:
        html = '''
        <h2>Update Product</h2>
        <form method="POST">
            Product ID: <strong>{{ product[0] }}</strong><br><br>
            Product Name: <input type="text" name="product_name" value="{{ product[1] }}"><br><br>
            Quantity: <input type="number" name="quantity" value="{{ product[2] }}"><br><br>
            <input type="submit" value="Update Product">
        </form>
        '''
        return render_template_string(html, product=product)
    else:
        return "Product not found."

if __name__ == "__main__":
    app.run(debug=True)
