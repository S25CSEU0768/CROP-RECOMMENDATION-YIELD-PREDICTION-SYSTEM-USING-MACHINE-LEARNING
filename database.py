"""
Database Management Module.
Provides secure user authentication, profile persistence, and advisory history tracking
using an embedded SQLite database with cryptographic password hashing.
"""

import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "agri_database.db")


@contextmanager
def get_db_connection():
    """Context manager for SQLite connection with dict-like row access that always closes cleanly."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initializes tables for users and advisory history if they do not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                state TEXT NOT NULL,
                district TEXT,
                land_area REAL NOT NULL,
                land_unit TEXT NOT NULL,
                investment_budget REAL NOT NULL,
                farming_goal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Advisory History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advisories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                recommended_crop TEXT NOT NULL,
                confidence REAL NOT NULL,
                yield_rate REAL NOT NULL,
                total_harvest REAL NOT NULL,
                gross_revenue REAL NOT NULL,
                net_profit REAL NOT NULL,
                roi_percent REAL NOT NULL,
                season TEXT NOT NULL,
                n_val REAL,
                p_val REAL,
                k_val REAL,
                temperature REAL,
                humidity REAL,
                ph REAL,
                rainfall REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()


def register_user(full_name, phone, password, state="Uttar Pradesh", district="Central",
                  land_area=5.0, land_unit="Acres", investment_budget=50000.0,
                  age=35, gender="Male", goal="Maximum Profitability"):
    """
    Securely registers a new farmer profile with hashed password.
    Returns (user_dict, error_message).
    """
    phone_clean = phone.strip()
    if not phone_clean or not password:
        return None, "Phone number and password are required."
        
    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    full_name, phone, password_hash, age, gender, state, district,
                    land_area, land_unit, investment_budget, farming_goal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                full_name.strip(), phone_clean, password_hash, age, gender,
                state.strip(), district.strip(), float(land_area), land_unit,
                float(investment_budget), goal
            ))
            user_id = cursor.lastrowid
            conn.commit()
            
        return get_user_by_id(user_id), None
    except sqlite3.IntegrityError:
        return None, "An account with this phone number already exists. Please login instead."
    except Exception as e:
        return None, str(e)


def authenticate_user(phone_or_name, password):
    """
    Authenticates a returning user against their hashed password.
    Returns (user_dict, error_message).
    """
    identifier = phone_or_name.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone = ? OR full_name = ?", (identifier, identifier))
        user = cursor.fetchone()
        
    if not user:
        return None, "No farmer account found with this phone number or name."
        
    if not check_password_hash(user["password_hash"], password):
        return None, "Incorrect password. Please try again."
        
    user_dict = dict(user)
    del user_dict["password_hash"]
    return user_dict, None


def get_user_by_id(user_id):
    """Retrieves a user profile by user ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
    if user:
        u = dict(user)
        del u["password_hash"]
        return u
    return None


def update_user_profile(user_id, investment_budget=None, land_area=None, land_unit=None):
    """
    Updates the investment budget and land parameters for a farmer profile.
    Returns (updated_user_dict, error_message).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            if investment_budget is not None:
                updates.append("investment_budget = ?")
                params.append(float(investment_budget))
            if land_area is not None:
                updates.append("land_area = ?")
                params.append(float(land_area))
            if land_unit is not None:
                updates.append("land_unit = ?")
                params.append(str(land_unit).strip())
                
            if not updates:
                return get_user_by_id(user_id), None
                
            params.append(int(user_id))
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
            
        updated = get_user_by_id(user_id)
        if not updated:
            return None, "User not found"
        return updated, None
    except Exception as e:
        return None, str(e)


def save_advisory(user_id, recommended_crop, confidence, yield_rate, total_harvest,
                  gross_revenue, net_profit, roi_percent, season, n, p, k, temp, hum, ph, rain):
    """Saves an inference advisory record linked to a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO advisories (
                    user_id, recommended_crop, confidence, yield_rate, total_harvest,
                    gross_revenue, net_profit, roi_percent, season,
                    n_val, p_val, k_val, temperature, humidity, ph, rainfall
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, recommended_crop, confidence, yield_rate, total_harvest,
                gross_revenue, net_profit, roi_percent, season,
                n, p, k, temp, hum, ph, rain
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error saving advisory: {e}")
        return None


def get_user_advisories(user_id, limit=10):
    """Returns past advisory records for a specific user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM advisories 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        
    return [dict(r) for r in rows]


# Initialize on import
init_db()
