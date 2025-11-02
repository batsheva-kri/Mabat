  CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month_year TEXT UNIQUE,
                    done INTEGER DEFAULT 0)
					
					SELECT id, typeof(id) FROM products
					
					DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image_path TEXT,
    category_id INTEGER,
    status TEXT,
    information TEXT,
    preferred_supplier_id INTEGER,
    price REAL,
    price_3 REAL,
    price_6 REAL,
    price_12 REAL
);