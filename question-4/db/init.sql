CREATE DATABASE customers_db;
CREATE DATABASE accounts_db;
CREATE DATABASE transactions_db;

\c customers_db;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO customers (first_name, last_name, email) VALUES
    ('Alice', 'Martin', 'alice.martin@email.com'),
    ('Bob', 'Dupont', 'bob.dupont@email.com');

\c accounts_db;

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'EUR',
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO accounts (customer_id, account_number, balance) VALUES
    (1, 'FR76-3000-0001', 5000.00),
    (1, 'FR76-3000-0002', 1200.50),
    (2, 'FR76-3000-0003', 850.00);

\c transactions_db;

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    from_account_id INTEGER,
    to_account_id INTEGER,
    amount DECIMAL(15, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
