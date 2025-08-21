# backward_fin.py

import psycopg2
from datetime import datetime

# Database connection details - UPDATE WITH YOUR CREDENTIALS
DB_NAME = "Finance Tracker"
DB_USER = "postgres"
DB_PASSWORD = "subhashini"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# ----------------- CREATE Operations -----------------

def create_asset(ticker, name, asset_class, price):
    """Adds a new asset to the assets table."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO assets (ticker_symbol, asset_name, asset_class, current_price) VALUES (%s, %s, %s, %s) ON CONFLICT (ticker_symbol) DO UPDATE SET current_price = EXCLUDED.current_price, asset_class = EXCLUDED.asset_class",
            (ticker, name, asset_class, price)
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error creating asset: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def create_transaction(ticker, date, type, shares, price, total_cost):
    """Adds a new transaction to the transactions table."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO transactions (ticker_symbol, transaction_date, transaction_type, shares, price_per_share, total_cost) VALUES (%s, %s, %s, %s, %s, %s)",
            (ticker, date, type, shares, price, total_cost)
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error creating transaction: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# ----------------- READ Operations -----------------

def read_all_assets():
    """Fetches all assets from the assets table."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT ticker_symbol, asset_name, asset_class, current_price FROM assets")
        assets = cur.fetchall()
        return assets
    except psycopg2.Error as e:
        print(f"Error reading assets: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def read_all_transactions():
    """Fetches all transactions from the transactions table."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT transaction_id, ticker_symbol, transaction_date, transaction_type, shares, price_per_share, total_cost FROM transactions ORDER BY transaction_date DESC")
        transactions = cur.fetchall()
        return transactions
    except psycopg2.Error as e:
        print(f"Error reading transactions: {e}")
        return []
    finally:
        cur.close()
        conn.close()
        
def read_portfolio_summary():
    """Calculates the total portfolio value and holdings by asset."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        SELECT 
            t.ticker_symbol,
            a.asset_name,
            a.asset_class,
            SUM(CASE WHEN t.transaction_type = 'buy' THEN t.shares ELSE -t.shares END) as total_shares,
            SUM(t.total_cost) AS total_cost_basis,
            a.current_price
        FROM transactions t
        JOIN assets a ON t.ticker_symbol = a.ticker_symbol
        GROUP BY t.ticker_symbol, a.asset_name, a.asset_class, a.current_price
        HAVING SUM(CASE WHEN t.transaction_type = 'buy' THEN t.shares ELSE -t.shares END) > 0;
        """
        cur.execute(query)
        summary = cur.fetchall()
        return summary
    except psycopg2.Error as e:
        print(f"Error reading portfolio summary: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# ----------------- UPDATE Operations -----------------

def update_asset_price(ticker, new_price):
    """Updates the current price of a specific asset."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE assets SET current_price = %s WHERE ticker_symbol = %s", (new_price, ticker))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error updating asset price: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# ----------------- DELETE Operations -----------------

def delete_transaction(transaction_id):
    """Deletes a transaction by its ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error deleting transaction: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# ----------------- Business Insights -----------------

def get_business_insights():
    """Provides key business insights using aggregation functions."""
    conn = get_db_connection()
    cur = conn.cursor()
    insights = {}
    try:
        # Count of unique assets
        cur.execute("SELECT COUNT(DISTINCT ticker_symbol) FROM assets")
        insights['total_unique_assets'] = cur.fetchone()[0]

        # Total number of transactions
        cur.execute("SELECT COUNT(*) FROM transactions")
        insights['total_transactions'] = cur.fetchone()[0]
        
        # Total cost of all buy transactions (SUM)
        cur.execute("SELECT SUM(total_cost) FROM transactions WHERE transaction_type = 'buy'")
        insights['total_buy_cost'] = cur.fetchone()[0]

        # Average cost per share for all transactions (AVG)
        cur.execute("SELECT AVG(price_per_share) FROM transactions")
        insights['avg_price_per_share'] = cur.fetchone()[0]

        # Most expensive transaction (MAX)
        cur.execute("SELECT MAX(total_cost) FROM transactions")
        insights['max_transaction_cost'] = cur.fetchone()[0]
        
        # Least expensive transaction (MIN)
        cur.execute("SELECT MIN(total_cost) FROM transactions")
        insights['min_transaction_cost'] = cur.fetchone()[0]
        
    except psycopg2.Error as e:
        print(f"Error fetching business insights: {e}")
        insights = {}
    finally:
        cur.close()
        conn.close()
    return insights