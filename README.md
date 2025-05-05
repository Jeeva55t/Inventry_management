📦 Warehouse Inventory Management System
This is a Flask-based web application for managing warehouse inventory, including product registration, product movement across locations, and viewing stock reports.

🔧 Features
User Registration & Login

Add Products (default to Warehouse)

Move Products between locations

View Inventory Report by Location

View Product Movement History (InTransit)

Add New Locations

🛠️ Tech Stack
Backend: Python, Flask

Database: MySQL

Frontend: HTML (Jinja2 templates), Bootstrap (optional)

Session Management: Flask Sessions

🗂️ Table Structure (MySQL)
1. users
sql
Copy
Edit
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);
2. products
sql
Copy
Edit
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
3. locations
sql
Copy
Edit
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
4. inventory
sql
Copy
Edit
CREATE TABLE inventory (
    product_id INT,
    location_id INT,
    quantity INT NOT NULL,
    PRIMARY KEY (product_id, location_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
5. movements
sql
Copy
Edit
CREATE TABLE movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    from_location_id INT,
    to_location_id INT,
    quantity INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (from_location_id) REFERENCES locations(id),
    FOREIGN KEY (to_location_id) REFERENCES locations(id)
);
🚀 Getting Started
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/warehouse-inventory.git
cd warehouse-inventory
2. Install Requirements
bash
Copy
Edit
pip install Flask mysqlclient
3. Configure Database
Start MySQL and create a database named inventory.

sql
Copy
Edit
CREATE DATABASE inventory;
USE inventory;
-- Then create tables as described above
Update DB credentials in app.py:

python
Copy
Edit
db = MySQLdb.connect(host="localhost", user="root", passwd="YOUR_PASSWORD", db="inventory")
4. Run the App
bash
Copy
Edit
python app.py
Navigate to: http://127.0.0.1:5000

📁 Directory Structure
arduino
Copy
Edit
/templates
    ├── login.html
    ├── register.html
    ├── home.html
    ├── add_product.html
    ├── move_products.html
    ├── report.html
    ├── in_transit.html
    └── add_location.html
app.py
README.md
🔐 Default Setup
Add a default location named warehouse via the Add Location page before adding products.

Products added will be stored in the warehouse by default.

Product movement updates quantities between locations and logs the transfer in the movements table.

📞 Contact
For issues or suggestions, contact jeevanandv63@gmail.com


## SCREENSHOTS:



https://github.com/user-attachments/assets/ed592aa1-9358-4363-93fd-9d5ca0889b34



![Screenshot 2025-05-05 192845](https://github.com/user-attachments/assets/9854e7f8-7a3a-40a8-84c5-d0fcefd907a3)
![Screenshot 2025-05-05 192824](https://github.com/user-attachments/assets/4bb88a23-29cf-4c21-845a-9ba2eef7ad71)
![Screenshot 2025-05-05 192756](https://github.com/user-attachments/assets/c73415f3-5916-488d-9d12-67fadd82d5ce)
![Screenshot 2025-05-05 192733](https://github.com/user-attachments/assets/5f4eb6b9-5398-4564-8c32-7fed43ac776f)
![Screenshot 2025-05-05 192715](https://github.com/user-attachments/assets/4630ddaa-a212-4a06-8081-858d59b1c5ce)
