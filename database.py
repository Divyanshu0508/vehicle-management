import sqlite3
from datetime import datetime
import hashlib

DB_NAME = "vehicle_customers_v6.db"
SALT = "workshop_secure_salt_2026"

def hash_password(password):
    """Hashes a password with a predefined salt using SHA-256 (matches auth.py)."""
    salted = password + SALT
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

import os
import streamlit as st

def is_postgres_configured():
    try:
        # Check streamlit secrets
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            return True
    except Exception:
        pass
    # Check environment variables
    if "DATABASE_URL" in os.environ:
        return True
    return False

def get_db_url():
    try:
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    return os.environ.get("DATABASE_URL")

class DatabaseRow:
    def __init__(self, data, colnames):
        self._data = dict(data)
        self._colnames = list(colnames)
        self._row_list = [self._data.get(col) for col in self._colnames]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row_list[key]
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

class DatabaseCursor:
    def __init__(self, cursor, is_postgres):
        self.cursor = cursor
        self.is_postgres = is_postgres
        self.lastrowid = None

    def execute(self, sql, params=None):
        if params is None:
            params = ()
        
        # Adapt placeholders
        if self.is_postgres:
            sql_adapted = sql.replace('?', '%s')
            
            # Handle lastrowid for INSERT
            if sql_adapted.strip().upper().startswith("INSERT INTO"):
                import re
                table_match = re.search(r"insert\s+into\s+([a-zA-Z0-9_\"`]+)", sql_adapted, re.IGNORECASE)
                table_name = table_match.group(1).strip('"`').lower() if table_match else ""
                
                if table_name != "users":
                    is_returning = "RETURNING" in sql_adapted.upper()
                    if not is_returning:
                        sql_adapted = sql_adapted.rstrip('; ')
                        sql_adapted += " RETURNING id"
                    
                    self.cursor.execute(sql_adapted, params)
                    res = self.cursor.fetchone()
                    if res:
                        if isinstance(res, dict):
                            self.lastrowid = res.get('id')
                        elif isinstance(res, (list, tuple)):
                            self.lastrowid = res[0]
                        else:
                            self.lastrowid = res
                    return self
            
            self.cursor.execute(sql_adapted, params)
        else:
            self.cursor.execute(sql, params)
            self.lastrowid = self.cursor.lastrowid
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        
        if self.is_postgres:
            colnames = [desc[0] for desc in self.cursor.description]
            if hasattr(row, 'keys') or isinstance(row, dict):
                return DatabaseRow(row, colnames)
            return DatabaseRow(zip(colnames, row), colnames)
        else:
            colnames = row.keys()
            return DatabaseRow(dict(row), colnames)

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return []
        
        results = []
        for r in rows:
            if self.is_postgres:
                colnames = [desc[0] for desc in self.cursor.description]
                if hasattr(r, 'keys') or isinstance(r, dict):
                    results.append(DatabaseRow(r, colnames))
                else:
                    results.append(DatabaseRow(zip(colnames, r), colnames))
            else:
                colnames = r.keys()
                results.append(DatabaseRow(dict(r), colnames))
        return results

    def close(self):
        self.cursor.close()

class DatabaseConnection:
    def __init__(self, conn, is_postgres):
        self.conn = conn
        self.is_postgres = is_postgres

    def cursor(self):
        if self.is_postgres:
            import psycopg2.extras
            return DatabaseCursor(self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor), is_postgres=True)
        else:
            return DatabaseCursor(self.conn.cursor(), is_postgres=False)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def execute(self, sql, *args, **kwargs):
        if self.is_postgres:
            if "PRAGMA" in sql.upper():
                return
            cursor = self.cursor()
            cursor.execute(sql, *args, **kwargs)
            return cursor
        else:
            return self.conn.execute(sql, *args, **kwargs)

try:
    import psycopg2
    DB_INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg2.IntegrityError)
except ImportError:
    DB_INTEGRITY_ERRORS = (sqlite3.IntegrityError,)

def get_db_connection():
    if is_postgres_configured():
        import psycopg2
        db_url = get_db_url()
        conn = psycopg2.connect(db_url)
        return DatabaseConnection(conn, is_postgres=True)
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return DatabaseConnection(conn, is_postgres=False)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    if conn.is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                customer_name TEXT,
                vehicle_number TEXT UNIQUE NOT NULL,
                vehicle_model TEXT NOT NULL,
                vehicle_color TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_records (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
                coating_date TEXT NOT NULL,
                payment_amount REAL NOT NULL DEFAULT 0.0,
                payment_status TEXT NOT NULL DEFAULT 'Pending',
                bill_number TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Staff'
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                vehicle_number TEXT UNIQUE NOT NULL,
                vehicle_model TEXT NOT NULL,
                vehicle_color TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                coating_date TEXT NOT NULL,
                payment_amount REAL NOT NULL DEFAULT 0.0,
                payment_status TEXT NOT NULL DEFAULT 'Pending',
                bill_number TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Staff'
            )
        """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "Admin"))
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("staff", hash_password("staff123"), "Staff"))
        conn.commit()

    conn.close()

def add_user(username, password_hash, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
        conn.commit()
        return True
    except DB_INTEGRITY_ERRORS:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_customer(customer_name, vehicle_number, vehicle_model, vehicle_color, coating_date, payment_amount, payment_status, bill_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First, insert customer profile
        cursor.execute("""
            INSERT INTO customers (
                customer_name, vehicle_number, vehicle_model, vehicle_color
            ) VALUES (?, ?, ?, ?)
        """, (customer_name, vehicle_number, vehicle_model, vehicle_color))
        
        customer_id = cursor.lastrowid
        
        # Second, insert initial coating visit
        cursor.execute("""
            INSERT INTO service_records (
                customer_id, coating_date, payment_amount, payment_status, bill_number
            ) VALUES (?, ?, ?, ?, ?)
        """, (customer_id, coating_date, payment_amount, payment_status, bill_number))
        
        conn.commit()
        return True, "Customer added successfully."
    except DB_INTEGRITY_ERRORS:
        return False, f"Vehicle number '{vehicle_number}' is already registered."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def add_visit(customer_id, coating_date, payment_amount, payment_status, bill_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO service_records (
                customer_id, coating_date, payment_amount, payment_status, bill_number
            ) VALUES (?, ?, ?, ?, ?)
        """, (customer_id, coating_date, payment_amount, payment_status, bill_number))
        conn.commit()
        return True, "Coating visit logged successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = [dict(row) for row in cursor.fetchall()]
    
    for cust in customers:
        # Fetch all visits for this customer ordered by ID ascending to ensure the first visit is chronological
        cursor.execute("""
            SELECT coating_date, bill_number, payment_amount 
            FROM service_records 
            WHERE customer_id = ? 
            ORDER BY id ASC
        """, (cust['id'],))
        visits = [dict(v) for v in cursor.fetchall()]
        
        if visits:
            # First visit is Coating Date
            cust['coating_dates'] = visits[0]['coating_date']
            cust['total_amount'] = sum(v['payment_amount'] for v in visits)
            
            # Combine bill numbers
            bills = [v['bill_number'] for v in visits if v['bill_number']]
            cust['bill_numbers'] = ", ".join(bills) if bills else ""
            
            # Subsquent visits are Free Buffing Dates
            if len(visits) > 1:
                buffing_dates = [v['coating_date'] for v in visits[1:]]
                cust['free_buffing_date'] = ", ".join(buffing_dates)
                cust['buffing_date'] = visits[-1]['coating_date'] # Latest visit date for sorting
            else:
                cust['free_buffing_date'] = ""
                cust['buffing_date'] = visits[0]['coating_date'] # First visit date for sorting
        else:
            cust['coating_dates'] = ""
            cust['total_amount'] = 0.0
            cust['bill_numbers'] = ""
            cust['free_buffing_date'] = ""
            cust['buffing_date'] = ""
            
    conn.close()
    
    # Sort by buffing_date / latest activity descending by default
    customers.sort(key=lambda x: x['buffing_date'], reverse=True)
    return customers

def get_customer_visits(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM service_records 
        WHERE customer_id = ? 
        ORDER BY coating_date DESC
    """, (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_customer(customer_id, customer_name, vehicle_number, vehicle_model, vehicle_color):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE customers
            SET customer_name = ?,
                vehicle_number = ?,
                vehicle_model = ?,
                vehicle_color = ?
            WHERE id = ?
        """, (customer_name, vehicle_number, vehicle_model, vehicle_color, customer_id))
        conn.commit()
        return True, "Customer profile details updated successfully."
    except DB_INTEGRITY_ERRORS:
        return False, f"Vehicle number '{vehicle_number}' is already registered by another customer."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_visit(visit_id, coating_date, payment_amount, payment_status, bill_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE service_records
            SET coating_date = ?,
                payment_amount = ?,
                payment_status = ?,
                bill_number = ?
            WHERE id = ?
        """, (coating_date, payment_amount, payment_status, bill_number, visit_id))
        conn.commit()
        return True, "Coating visit updated successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        return True, "Customer profile and all coating history deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_visit(visit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM service_records WHERE id = ?", (visit_id,))
        conn.commit()
        return True, "Coating visit deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total unique customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    
    # Total registered vehicles (should match total customers in this design)
    total_vehicles = total_customers
    
    # Total collections (where status != Pending)
    cursor.execute("SELECT SUM(payment_amount) FROM service_records WHERE payment_status != 'Pending'")
    val = cursor.fetchone()[0]
    total_collections = val if val else 0.0
    
    # Pending payments count
    cursor.execute("SELECT COUNT(*) FROM service_records WHERE payment_status = 'Pending'")
    pending_payments = cursor.fetchone()[0]
    
    conn.close()
    return total_customers, total_vehicles, total_collections, pending_payments

def get_unique_models():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT vehicle_model FROM customers")
    models = [row['vehicle_model'] for row in cursor.fetchall() if row['vehicle_model']]
    conn.close()
    return models

def get_unique_colors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT vehicle_color FROM customers")
    colors = [row['vehicle_color'] for row in cursor.fetchall() if row['vehicle_color']]
    conn.close()
    return colors

