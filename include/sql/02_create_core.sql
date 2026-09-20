CREATE SCHEMA IF NOT EXISTS core;


CREATE TABLE IF NOT EXISTS core.customers (
    customerid      TEXT PRIMARY KEY,
    customername    TEXT NOT NULL,
    segment         TEXT,
    country         TEXT,
    city            TEXT,
    state           TEXT,
    postal_code     TEXT,
    region          TEXT
);


CREATE TABLE IF NOT EXISTS core.products (
    productid       TEXT PRIMARY KEY,
    category        TEXT,
    subcategory     TEXT,
    product_name    TEXT
);


CREATE TABLE IF NOT EXISTS core.orders (
    rowid           BIGINT PRIMARY KEY,
    orderid         TEXT NOT NULL,
    customerid      TEXT NOT NULL REFERENCES core.customers(customerid),
    productid       TEXT NOT NULL REFERENCES core.products(productid),
    orderdate       DATE,
    shipdate        DATE,
    shipmode        TEXT,
    sales           NUMERIC(12, 2),
    quantity        INTEGER,
    discount        NUMERIC(5, 4),
    profit          NUMERIC(12, 2),
    deliverytime    INTEGER,
    profit_margin   NUMERIC(6, 4)
);


CREATE INDEX IF NOT EXISTS idx_orders_customerid ON core.orders(customerid);
CREATE INDEX IF NOT EXISTS idx_orders_productid  ON core.orders(productid);
CREATE INDEX IF NOT EXISTS idx_orders_orderid     ON core.orders(orderid);
