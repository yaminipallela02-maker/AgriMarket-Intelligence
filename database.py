import os
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime
from pathlib import Path

# MySQL Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DB = os.getenv("MYSQL_DB", "agrimarket")

# SQLite Fallback Configuration
BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB = BASE_DIR / "agrimarket.db"

_db_engine = None  # "mysql" or "sqlite"

def get_db_type():
    """Returns whether MySQL or SQLite is currently active."""
    global _db_engine
    if _db_engine is None:
        init_db()
    return "MySQL 8.0" if _db_engine == "mysql" else "SQLite (Fallback)"


def create_connection():
    """
    Connect to MySQL database. If MySQL is unavailable, automatically
    fallback to SQLite agrimarket.db so the app never crashes.
    """
    global _db_engine
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        _db_engine = "mysql"
        return conn
    except Exception as e:
        _db_engine = "sqlite"
        conn = sqlite3.connect(str(SQLITE_DB), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def get_connection():
    return create_connection()


def _execute(conn, query, params=None):
    """
    Execute query adapting %s for MySQL and ? for SQLite transparently.
    """
    global _db_engine
    params = params or ()
    
    if _db_engine == "sqlite":
        sqlite_query = query.replace("%s", "?")
        cursor = conn.cursor()
        cursor.execute(sqlite_query, params)
        conn.commit()
        return cursor
    else:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor


def _fetchall(conn, query, params=None):
    cursor = _execute(conn, query, params)
    rows = cursor.fetchall()
    return [dict(r) for r in rows] if rows else []


def _fetchone(conn, query, params=None):
    cursor = _execute(conn, query, params)
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(row)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """Ensure database and tables are created."""
    global _db_engine
    
    try:
        import pymysql
        srv = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=True
        )
        with srv.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        srv.close()
        _db_engine = "mysql"
    except Exception:
        _db_engine = "sqlite"

    conn = create_connection()
    try:
        if _db_engine == "mysql":
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        phone VARCHAR(50) UNIQUE,
                        firebase_uid VARCHAR(255) UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS crops (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        crop_name VARCHAR(100) NOT NULL,
                        planting_date VARCHAR(50),
                        land_area FLOAT DEFAULT 1.0,
                        expected_harvest_date VARCHAR(50),
                        water_source VARCHAR(100),
                        pesticide_usage VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS crop_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        crop_name VARCHAR(100),
                        quantity FLOAT DEFAULT 0,
                        harvest_date VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        prediction_type VARCHAR(100) NOT NULL,
                        crop_name VARCHAR(100) NOT NULL,
                        predicted_value FLOAT,
                        prediction_date VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        crop_name VARCHAR(100) NOT NULL,
                        buyer_name VARCHAR(255) NOT NULL,
                        quantity FLOAT NOT NULL,
                        price FLOAT NOT NULL,
                        total_amount FLOAT NOT NULL,
                        transaction_date VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS profiles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT UNIQUE NOT NULL,
                        phone VARCHAR(50),
                        location VARCHAR(255),
                        village VARCHAR(255),
                        district VARCHAR(255),
                        state VARCHAR(255),
                        land_area FLOAT DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
        else:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    phone TEXT UNIQUE,
                    firebase_uid TEXT UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crop_name TEXT NOT NULL,
                    planting_date TEXT,
                    land_area REAL,
                    expected_harvest_date TEXT,
                    water_source TEXT,
                    pesticide_usage TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crop_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crop_name TEXT,
                    quantity REAL DEFAULT 0,
                    harvest_date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    prediction_type TEXT NOT NULL,
                    crop_name TEXT NOT NULL,
                    predicted_value REAL,
                    prediction_date TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crop_name TEXT NOT NULL,
                    buyer_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    transaction_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    phone TEXT,
                    location TEXT,
                    village TEXT,
                    district TEXT,
                    state TEXT,
                    land_area REAL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            conn.commit()
    finally:
        conn.close()


# Password helpers: PBKDF2-HMAC-SHA256 with a unique random salt.
def _hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt.encode("utf-8"), 260000).hex()
    return f"pbkdf2_sha256${salt}${digest}"

def _verify_password(password, stored_value):
    if not stored_value:
        return False
    if stored_value.startswith("pbkdf2_sha256$"):
        try:
            _, salt, expected = stored_value.split("$", 2)
            actual = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt.encode("utf-8"), 260000).hex()
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False
    # Backward compatibility: allow old plaintext accounts once, then upgrade.
    return hmac.compare_digest(str(password), str(stored_value))

# ============================================================
# USER MANAGEMENT
# ============================================================

def register_user(name, email, password, phone=None, firebase_uid=None):
    """Register farmer account with complete phone and firebase UID support."""
    name = str(name or "").strip()
    email = str(email or "").strip().lower()
    if not name or not email or not password:
        return None
    conn = create_connection()
    try:
        phone_clean = None
        if phone:
            p = str(phone).strip().replace(" ", "")
            if not p.startswith("+") and len(p) == 10:
                phone_clean = "+91" + p
            else:
                phone_clean = p

        # Check existing email
        existing_email = _fetchone(conn, "SELECT id FROM users WHERE email = %s", (email,))
        if existing_email:
            return None

        # Check existing phone
        if phone_clean:
            existing_phone = _fetchone(conn, "SELECT id FROM users WHERE phone = %s", (phone_clean,))
            if existing_phone:
                return existing_phone["id"]

        cursor = _execute(
            conn,
            "INSERT INTO users (name, email, password, phone, firebase_uid) VALUES (%s, %s, %s, %s, %s)",
            (name, email, _hash_password(password), phone_clean, firebase_uid)
        )
        new_id = cursor.lastrowid
        
        try:
            _execute(
                conn,
                "INSERT INTO profiles (user_id, phone, location, land_area) VALUES (%s, %s, 'Andhra Pradesh', 2.5)",
                (new_id, phone_clean or "")
            )
        except Exception:
            pass

        seed_starter_crops_for_user(new_id)
        return new_id
    except Exception as e:
        print("Registration error:", e)
        return None
    finally:
        conn.close()


def add_user(name, email, password):
    return bool(register_user(name, email, password))


def get_user(email, password):
    """Authenticate a user and transparently upgrade legacy plaintext passwords."""
    conn = create_connection()
    try:
        row = _fetchone(
            conn,
            "SELECT id, name, email, password, phone, firebase_uid FROM users WHERE email = %s",
            (str(email).strip().lower(),)
        )
        if not row or not _verify_password(password, row.get("password")):
            return None

        # Upgrade old plaintext passwords after a successful login.
        if not str(row.get("password", "")).startswith("pbkdf2_sha256$"):
            _execute(
                conn,
                "UPDATE users SET password = %s WHERE id = %s",
                (_hash_password(password), row["id"])
            )

        row.pop("password", None)
        return row
    finally:
        conn.close()


def login_user(email, password):
    user = get_user(email, password)
    if user:
        return (user["id"], user["name"], user["email"])
    return None


def get_user_by_id(user_id):
    conn = create_connection()
    try:
        return _fetchone(
            conn,
            "SELECT id, name, email, phone, firebase_uid FROM users WHERE id = %s",
            (user_id,)
        )
    finally:
        conn.close()


def get_user_by_phone(phone):
    if not phone:
        return None
    p_str = str(phone).strip().replace(" ", "")
    p_plain = p_str.replace("+91", "").strip()
    p_with = "+91" + p_plain
    
    conn = create_connection()
    try:
        return _fetchone(
            conn,
            "SELECT id, name, email, phone, firebase_uid FROM users WHERE phone = %s OR phone = %s",
            (p_with, p_plain)
        )
    finally:
        conn.close()


def get_user_by_firebase_uid(firebase_uid):
    if not firebase_uid:
        return None
    conn = create_connection()
    try:
        return _fetchone(
            conn,
            "SELECT id, name, email, phone, firebase_uid FROM users WHERE firebase_uid = %s",
            (str(firebase_uid).strip(),)
        )
    finally:
        conn.close()


def create_phone_user(name, phone, firebase_uid=None):
    name = (name or "").strip()
    phone = (phone or "").strip()
    
    if not phone.startswith("+") and len(phone) == 10:
        phone = "+91" + phone
        
    if not name:
        name = f"Farmer {phone[-4:] if len(phone) >= 4 else 'User'}"

    firebase_uid = (firebase_uid or f"PHONE_{phone.replace('+', '')}").strip()
    email = f"farmer_{phone.replace('+', '')}@agrimarket.in"
    password = f"OTP_VERIFIED:{firebase_uid[:16]}"

    conn = create_connection()
    try:
        existing = get_user_by_phone(phone)
        if existing:
            _execute(
                conn,
                "UPDATE users SET firebase_uid = %s, name = COALESCE(%s, name) WHERE id = %s",
                (firebase_uid, name, existing["id"])
            )
            seed_starter_crops_for_user(existing["id"])
            return existing["id"]

        cursor = _execute(
            conn,
            "INSERT INTO users (name, email, password, phone, firebase_uid) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, phone, firebase_uid)
        )
        new_id = cursor.lastrowid
        
        try:
            _execute(
                conn,
                "INSERT INTO profiles (user_id, phone, location, land_area) VALUES (%s, %s, 'Andhra Pradesh', 2.0)",
                (new_id, phone)
            )
        except Exception:
            pass

        seed_starter_crops_for_user(new_id)
        return new_id
    except Exception as e:
        print("Error creating phone user:", e)
        u = get_user_by_phone(phone)
        return u["id"] if u else None
    finally:
        conn.close()


def seed_starter_crops_for_user(user_id):
    """Ensure user always has standard starter crops for realistic demonstration."""
    if not user_id:
        return
    conn = create_connection()
    try:
        existing = _fetchall(conn, "SELECT id FROM crops WHERE user_id = %s", (user_id,))
        if len(existing) == 0:
            starters = [
                (user_id, 'Rice (BPT-5204)', '2026-08-15', 3.5, '2026-11-30', 'Canal', 'Low'),
                (user_id, 'Tomato (Hybrid)', '2026-09-01', 2.0, '2026-12-15', 'Borewell', 'Medium'),
                (user_id, 'Guntur Chilli', '2026-08-20', 1.5, '2026-12-28', 'Drip Irrigation', 'Low'),
                (user_id, 'Cotton', '2026-07-10', 4.0, '2026-12-20', 'Canal', 'Medium')
            ]
            for s in starters:
                _execute(
                    conn,
                    """
                    INSERT INTO crops (user_id, crop_name, planting_date, land_area, expected_harvest_date, water_source, pesticide_usage)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    s
                )
    except Exception as e:
        print("Notice seeding starter crops:", e)
    finally:
        conn.close()


# ============================================================
# CROPS MANAGEMENT
# ============================================================

def add_crop(user_id, crop_name, planting_date, land_area, expected_harvest_date, water_source, pesticide_usage):
    conn = create_connection()
    try:
        cursor = _execute(
            conn,
            """
            INSERT INTO crops (user_id, crop_name, planting_date, land_area, expected_harvest_date, water_source, pesticide_usage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, str(crop_name), str(planting_date), float(land_area), str(expected_harvest_date), str(water_source), str(pesticide_usage))
        )
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_crops(user_id):
    """Retrieve user crops, auto-seeding if account is brand new."""
    if not user_id:
        return []
    conn = create_connection()
    try:
        crops = _fetchall(
            conn,
            "SELECT * FROM crops WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
        if not crops:
            seed_starter_crops_for_user(user_id)
            crops = _fetchall(
                conn,
                "SELECT * FROM crops WHERE user_id = %s ORDER BY id DESC",
                (user_id,)
            )
        return crops
    finally:
        conn.close()


def get_all_crops():
    """Retrieve all crops in database across all users for demo overview."""
    conn = create_connection()
    try:
        return _fetchall(
            conn,
            """
            SELECT c.*, u.name as farmer_name, u.phone as farmer_phone
            FROM crops c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.id DESC
            """
        )
    finally:
        conn.close()


def get_latest_crop(user_id):
    conn = create_connection()
    try:
        return _fetchone(
            conn,
            "SELECT * FROM crops WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            (user_id,)
        )
    finally:
        conn.close()


def delete_crop(crop_id, user_id=None):
    conn = create_connection()
    try:
        if user_id:
            _execute(conn, "DELETE FROM crops WHERE id = %s AND user_id = %s", (crop_id, user_id))
        else:
            _execute(conn, "DELETE FROM crops WHERE id = %s", (crop_id,))
        return True
    finally:
        conn.close()


# ============================================================
# CROP HISTORY
# ============================================================

def add_crop_history(user_id, crop_name, quantity=0, harvest_date=None):
    if harvest_date is None:
        harvest_date = datetime.now().strftime("%Y-%m-%d")
    conn = create_connection()
    try:
        cursor = _execute(
            conn,
            "INSERT INTO crop_history (user_id, crop_name, quantity, harvest_date) VALUES (%s, %s, %s, %s)",
            (user_id, str(crop_name), float(quantity), str(harvest_date))
        )
        return cursor.lastrowid
    finally:
        conn.close()


def get_crop_history(user_id):
    conn = create_connection()
    try:
        return _fetchall(
            conn,
            "SELECT * FROM crop_history WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
    finally:
        conn.close()


# ============================================================
# PREDICTIONS
# ============================================================

def save_prediction(user_id, prediction_type, crop_name, predicted_value):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = create_connection()
    try:
        cursor = _execute(
            conn,
            """
            INSERT INTO predictions (user_id, prediction_type, crop_name, predicted_value, prediction_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, str(prediction_type), str(crop_name), float(predicted_value), today)
        )
        return cursor.lastrowid
    finally:
        conn.close()


def get_predictions(user_id):
    conn = create_connection()
    try:
        return _fetchall(
            conn,
            "SELECT * FROM predictions WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
    finally:
        conn.close()


# ============================================================
# TRANSACTIONS
# ============================================================

def add_transaction(user_id, crop_name, buyer_name, quantity, price, status="Completed"):
    qty = float(quantity)
    prc = float(price)
    total_amount = round(qty * prc, 2)
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = create_connection()
    try:
        cursor = _execute(
            conn,
            """
            INSERT INTO transactions (user_id, crop_name, buyer_name, quantity, price, total_amount, transaction_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, str(crop_name), str(buyer_name), qty, prc, total_amount, today, str(status))
        )
        return cursor.lastrowid
    finally:
        conn.close()


def get_transactions(user_id):
    conn = create_connection()
    try:
        trans = _fetchall(
            conn,
            "SELECT * FROM transactions WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
        if not trans and user_id:
            _execute(
                conn,
                """
                INSERT INTO transactions (user_id, crop_name, buyer_name, quantity, price, total_amount, transaction_date, status)
                VALUES (%s, 'Rice', 'Guntur Mandi Traders', 40, 2600, 104000, '2026-10-25', 'Completed'),
                       (%s, 'Tomato', 'Reliance Fresh Mart', 25, 2800, 70000, '2026-11-01', 'Completed')
                """,
                (user_id, user_id)
            )
            trans = _fetchall(conn, "SELECT * FROM transactions WHERE user_id = %s ORDER BY id DESC", (user_id,))
        return trans
    finally:
        conn.close()


# ============================================================
# PROFILES
# ============================================================

def save_profile(user_id, phone, location, village, district, state, land_area):
    conn = create_connection()
    try:
        existing = _fetchone(conn, "SELECT id FROM profiles WHERE user_id = %s", (user_id,))
        if existing:
            _execute(
                conn,
                """
                UPDATE profiles
                SET phone = %s, location = %s, village = %s, district = %s, state = %s, land_area = %s
                WHERE user_id = %s
                """,
                (str(phone), str(location), str(village), str(district), str(state), float(land_area), user_id)
            )
        else:
            _execute(
                conn,
                """
                INSERT INTO profiles (user_id, phone, location, village, district, state, land_area)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, str(phone), str(location), str(village), str(district), str(state), float(land_area))
            )
        return True
    finally:
        conn.close()


def get_profile(user_id):
    conn = create_connection()
    try:
        return _fetchone(
            conn,
            "SELECT * FROM profiles WHERE user_id = %s",
            (user_id,)
        )
    finally:
        conn.close()