import sqlite3
from datetime import datetime
import hashlib

DB_NAME = "vehicle_customers_v6.db"
SALT = "workshop_secure_salt_2026"

def hash_password(password):
    """Hashes a password with a predefined salt using SHA-256 (matches auth.py)."""
    salted = password + SALT
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create customers table (Profile Info)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            vehicle_number TEXT UNIQUE NOT NULL,
            vehicle_model TEXT NOT NULL,
            vehicle_color TEXT NOT NULL
        )
    """)
    # Create service_records table (Visits Info)
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
    # Create users table (Auth Info)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Staff'
        )
    """)
    conn.commit()

    # Seed default user accounts if table is empty
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
    except sqlite3.IntegrityError:
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
    except sqlite3.IntegrityError:
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
    except sqlite3.IntegrityError:
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

