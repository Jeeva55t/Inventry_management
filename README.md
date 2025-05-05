
# 📦 Warehouse Inventory Management System

This is a Flask-based web application for managing warehouse inventory, including product registration, product movement across locations, and viewing stock reports.

## 🔧 Features

- User Registration & Login
- Add Products (default to Warehouse)
- Move Products between locations
- View Inventory Report by Location
- View Product Movement History (InTransit)
- Add New Locations

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML (Jinja2 templates), Bootstrap (optional)
- **Session Management**: Flask Sessions

## 🗂️ Table Structure (MySQL)

### 1. `users`
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);
```

### 2. `products`
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

### 3. `locations`
```sql
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

### 4. `inventory`
```sql
CREATE TABLE inventory (
    product_id INT,
    location_id INT,
    quantity INT NOT NULL,
    PRIMARY KEY (product_id, location_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
```

### 5. `movements`
```sql
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
```

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/warehouse-inventory.git
cd warehouse-inventory
```

### 2. Install Requirements
```bash
pip install Flask mysqlclient
```

### 3. Configure Database

- Start MySQL and create a database named `inventory`.
```sql
CREATE DATABASE inventory;
USE inventory;
-- Then create tables as described above
```

- Update DB credentials in `app.py`.

### 4. Run the App
```bash
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
