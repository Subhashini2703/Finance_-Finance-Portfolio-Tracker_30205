CREATE TABLE assets (
    ticker_symbol VARCHAR(10) PRIMARY KEY,
    asset_name VARCHAR(100) NOT NULL,
    asset_class VARCHAR(50) NOT NULL,
    current_price DECIMAL(15, 2)
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    ticker_symbol VARCHAR(10) REFERENCES assets(ticker_symbol),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(10) NOT NULL, -- 'buy', 'sell', 'dividend'
    shares DECIMAL(15, 4) NOT NULL,
    price_per_share DECIMAL(15, 2) NOT NULL,
    total_cost DECIMAL(15, 2) NOT NULL
);
INSERT INTO assets (ticker_symbol, asset_name, asset_class, current_price) VALUES
('AAPL', 'Apple Inc.', 'Equity', 200.50),
('GOOGL', 'Alphabet Inc.', 'Equity', 150.75),
('TSLA', 'Tesla, Inc.', 'Equity', 250.00),
('BTC', 'Bitcoin', 'Crypto', 65000.00),
('SPY', 'SPDR S&P 500 ETF Trust', 'Equity', 500.25);
INSERT INTO transactions (ticker_symbol, transaction_date, transaction_type, shares, price_per_share, total_cost) VALUES
('AAPL', '2024-01-15', 'buy', 10.0, 185.50, 1855.00),
('GOOGL', '2024-02-20', 'buy', 5.0, 145.00, 725.00),
('TSLA', '2024-03-10', 'buy', 2.5, 240.00, 600.00),
('AAPL', '2024-04-05', 'buy', 5.0, 195.25, 976.25),
('BTC', '2024-05-01', 'buy', 0.1, 62000.00, 6200.00),
('SPY', '2024-06-12', 'buy', 3.0, 490.50, 1471.50),
('AAPL', '2024-07-20', 'dividend', 0.0, 0.24, 2.40);