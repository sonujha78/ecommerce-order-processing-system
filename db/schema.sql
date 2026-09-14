CREATE DATABASE IF NOT EXISTS ordersDB;
USE ordersDB;

CREATE TABLE products (
    product_id   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    stock_qty    INT NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT NOT NULL,
    status       ENUM('received','processing','confirmed','failed') NOT NULL DEFAULT 'received',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE order_events (
    event_id    INT AUTO_INCREMENT PRIMARY KEY,
    order_id    INT NOT NULL,
    event_type  VARCHAR(100) NOT NULL,
    payload     JSON NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO products (name, price, stock_qty) VALUES
('Wireless Mouse', 799.00, 50),
('Mechanical Keyboard', 3499.00, 30),
('Last-Item Widget', 199.00, 1);
