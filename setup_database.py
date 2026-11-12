import pymysql
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB = BASE_DIR / "agrimarket.db"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "agrimarket"

print("--- INITIALIZING MYSQL DATABASE ---")
try:
    # 1. Connect without db to create database
    server_conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=True
    )
    with server_conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database `{MYSQL_DB}` ensured.")
    server_conn.close()

    # 2. Connect to agrimarket db
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cur:
        # Create users table
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

        # Create crops table
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

        # Create crop_history table
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

        # Create predictions table
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

        # Create transactions table
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

        # Create profiles table
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

        print("All MySQL tables successfully created.")

        # Check existing users in MySQL
        cur.execute("SELECT COUNT(*) AS cnt FROM users;")
        user_count = cur.fetchone()["cnt"]

        # If empty, migrate from SQLite if sqlite exists
        if user_count == 0 and SQLITE_DB.exists():
            print("Migrating records from SQLite to MySQL...")
            s_conn = sqlite3.connect(str(SQLITE_DB))
            s_conn.row_factory = sqlite3.Row
            s_cur = s_conn.cursor()

            try:
                s_users = s_cur.execute("SELECT * FROM users").fetchall()
                for u in s_users:
                    u_dict = dict(u)
                    cur.execute("""
                        INSERT IGNORE INTO users (id, name, email, password, phone, firebase_uid)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        u_dict.get("id"),
                        u_dict.get("name"),
                        u_dict.get("email"),
                        u_dict.get("password"),
                        u_dict.get("phone"),
                        u_dict.get("firebase_uid")
                    ))
                print(f"Migrated {len(s_users)} users.")

                s_crops = s_cur.execute("SELECT * FROM crops").fetchall()
                for c in s_crops:
                    c_dict = dict(c)
                    cur.execute("""
                        INSERT IGNORE INTO crops (id, user_id, crop_name, planting_date, land_area, expected_harvest_date, water_source, pesticide_usage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        c_dict.get("id"),
                        c_dict.get("user_id"),
                        c_dict.get("crop_name"),
                        c_dict.get("planting_date"),
                        c_dict.get("land_area"),
                        c_dict.get("expected_harvest_date"),
                        c_dict.get("water_source"),
                        c_dict.get("pesticide_usage")
                    ))
                print(f"Migrated {len(s_crops)} crops.")

                s_trans = s_cur.execute("SELECT * FROM transactions").fetchall()
                for t in s_trans:
                    t_dict = dict(t)
                    cur.execute("""
                        INSERT IGNORE INTO transactions (id, user_id, crop_name, buyer_name, quantity, price, total_amount, transaction_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        t_dict.get("id"),
                        t_dict.get("user_id"),
                        t_dict.get("crop_name"),
                        t_dict.get("buyer_name"),
                        t_dict.get("quantity"),
                        t_dict.get("price"),
                        t_dict.get("total_amount"),
                        t_dict.get("transaction_date"),
                        t_dict.get("status")
                    ))
                print(f"Migrated {len(s_trans)} transactions.")
            except Exception as e:
                print("Notice during SQLite migration:", e)
            finally:
                s_conn.close()

        # Check if default demo user exists
        cur.execute("SELECT * FROM users WHERE phone = '+919876543210' OR id = 1 LIMIT 1;")
        demo_user = cur.fetchone()
        if not demo_user:
            cur.execute("""
                INSERT INTO users (name, email, password, phone, firebase_uid)
                VALUES ('Yamini Farmer', 'farmer@agrimarket.local', 'farmer123', '+919876543210', 'DEMO_FARMER_UID_101');
            """)
            demo_user_id = cur.lastrowid
            print(f"Created demo farmer account with ID: {demo_user_id}")
            # Add initial crop
            cur.execute("""
                INSERT INTO crops (user_id, crop_name, planting_date, land_area, expected_harvest_date, water_source, pesticide_usage)
                VALUES (%s, 'Rice', '2026-08-10', 3.5, '2026-11-25', 'Canal', 'Low'),
                       (%s, 'Tomato', '2026-09-01', 2.0, '2026-12-15', 'Borewell', 'Medium');
            """, (demo_user_id, demo_user_id))
            # Add initial transaction
            cur.execute("""
                INSERT INTO transactions (user_id, crop_name, buyer_name, quantity, price, total_amount, transaction_date, status)
                VALUES (%s, 'Rice', 'Guntur Agro Traders', 50, 2550, 127500, '2026-10-20', 'Completed');
            """, (demo_user_id,))
            # Add profile
            cur.execute("""
                INSERT INTO profiles (user_id, phone, location, village, district, state, land_area)
                VALUES (%s, '+919876543210', 'Andhra Pradesh', 'Malleswaram', 'Krishna', 'Andhra Pradesh', 5.5);
            """, (demo_user_id,))

    conn.close()
    print("SUCCESS: MySQL Database initialized and ready!")

except Exception as ex:
    print("MySQL Error:", ex)
