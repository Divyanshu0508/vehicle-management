import sqlite3
from datetime import datetime

DB_NAME = "customers.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            vehicle_model TEXT NOT NULL,
            vehicle_color TEXT NOT NULL,
            record_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_customer(customer_name, mobile_number, vehicle_number, vehicle_type, vehicle_model, vehicle_color, record_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO customers (
                customer_name, mobile_number, vehicle_number, vehicle_type, vehicle_model, vehicle_color, record_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_name, mobile_number, vehicle_number, vehicle_type, vehicle_model, vehicle_color, record_date))
        conn.commit()
        return True, "Customer added successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY record_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_customer(customer_id, customer_name, mobile_number, vehicle_number, vehicle_type, vehicle_model, vehicle_color, record_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE customers
            SET customer_name = ?,
                mobile_number = ?,
                vehicle_number = ?,
                vehicle_type = ?,
                vehicle_model = ?,
                vehicle_color = ?,
                record_date = ?
            WHERE id = ?
        """, (customer_name, mobile_number, vehicle_number, vehicle_type, vehicle_model, vehicle_color, record_date, customer_id))
        conn.commit()
        return True, "Customer details updated successfully."
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
        return True, "Customer deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
