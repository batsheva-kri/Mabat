PRAGMA foreign_keys = ON;

-- ===================
-- Lookup Tables
-- ===================
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

-- ===================
-- Users & Roles
-- ===================
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name TEXT NOT NULL UNIQUE,
  password_ TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('manager','worker','general'))
);

-- ===================
-- Suppliers
-- ===================
CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  phone TEXT,
  email TEXT
);

-- ===================
-- Products
-- ===================
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  image_path TEXT,
  category_id INTEGER,
  status TEXT NOT NULL CHECK(status IN ('inventory','invitation')) DEFAULT 'inventory',
  information TEXT,
  preferred_supplier_id INTEGER,
  FOREIGN KEY(category_id) REFERENCES categories(id),
  FOREIGN KEY(preferred_supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

-- ===================
-- Catalog
-- ===================
CREATE TABLE IF NOT EXISTS catalog (
  product_id INTEGER PRIMARY KEY,
  price REAL,
  price_3 REAL,
  price_6 REAL,
  price_12 REAL,
  FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ===================
-- Suppliers Catalog (Unique per supplier+product)
-- ===================
CREATE TABLE IF NOT EXISTS suppliers_catalog (
  supplier_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  price REAL,
  PRIMARY KEY (supplier_id, product_id),
  FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);
-- ===================
-- Supplier Reports
-- ===================
CREATE TABLE IF NOT EXISTS supplier_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_id INTEGER NOT NULL,
  date_ TEXT,
  product_id INTEGER,
  count_  INTEGER,
  calc REAL,
  FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
  FOREIGN KEY(product_id) REFERENCES products(id)
);

-- ===================
-- Customers
-- ===================
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  notes TEXT
);

-- ===================
-- Customer Invitations & Items
-- ===================
CREATE TABLE IF NOT EXISTS customer_invitations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER,
  created_by_user_id INTEGER,
  date_ TEXT,
  notes TEXT,
  total_price REAL,
  status TEXT CHECK(status IN ('open', 'invented', 'in_shop', 'collected')) DEFAULT 'open',
  call INTEGER DEFAULT 0,
  FOREIGN KEY(customer_id) REFERENCES customers(id),
  FOREIGN KEY(created_by_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS customer_invitation_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invitation_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  supplied INTEGER DEFAULT 0, -- לשנות לבולאין
  price REAL,
  size TEXT,
  FOREIGN KEY(invitation_id) REFERENCES customer_invitations(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

-- ===================
-- Supplier Invitations & Items
-- ===================
CREATE TABLE IF NOT EXISTS supplier_invitations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_id INTEGER NOT NULL,
  date_ TEXT,
  supplied INTEGER DEFAULT 0,
  notes TEXT,
  product_id INTEGER NOT NULL,
  size TEXT,
  quantity INTEGER NOT NULL DEFAULT 1,
  customer_invitation_id INTEGER,
  close INTEGER DEFAULT 0,
  FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
  FOREIGN KEY(product_id) REFERENCES products(id),
  FOREIGN KEY(customer_invitation_id) REFERENCES customer_invitations(id)
);

-- ===================
-- Worker Reports
-- ===================
CREATE TABLE IF NOT EXISTS worker_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date_ TEXT,
  enter_time TEXT,
  exit_time TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ===================
-- Required Stock
-- ===================
CREATE TABLE IF NOT EXISTS required_stock (
  product_id INTEGER PRIMARY KEY,
  required_count INTEGER NOT NULL,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

-- ===================
-- Indexes for Performance
-- ===================
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(preferred_supplier_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name);
CREATE INDEX IF NOT EXISTS idx_custinv_customer ON customer_invitations(customer_id);
CREATE INDEX IF NOT EXISTS idx_custinv_date ON customer_invitations(date_);
CREATE INDEX IF NOT EXISTS idx_custinvitems_inv ON customer_invitation_items(invitation_id);
CREATE INDEX IF NOT EXISTS idx_suppinv_supplier ON supplier_invitations(supplier_id);
CREATE INDEX IF NOT EXISTS idx_workerreports_user ON worker_reports(user_id);
