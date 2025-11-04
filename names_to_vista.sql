CREATE TABLE name_products_to_vista (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code INTEGER NOT NULL,
    units_per_box INTEGER NOT NULL,   -- לדוגמה: 6 / 30 / 90
    package_name TEXT,                -- אופציונלי: "קופסה קטנה", "קופסה גדולה"
    FOREIGN KEY (product_code) REFERENCES products(id)
);
