import sqlite3
from datetime import datetime


# ============================================================
# DATABASE FILE
# ============================================================

DATABASE_NAME = "agrimarket.db"


# ============================================================
# CREATE DATABASE CONNECTION
# ============================================================

def create_connection():

    conn = sqlite3.connect(
        DATABASE_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# GET CONNECTION
# ============================================================

def get_connection():

    return create_connection()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    create_tables()


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = create_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # CROPS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crops (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            crop_name TEXT NOT NULL,

            planting_date TEXT,

            land_area REAL,

            expected_harvest_date TEXT,

            water_source TEXT,

            pesticide_usage TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # --------------------------------------------------------
    # CROP HISTORY TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            crop_name TEXT NOT NULL,

            quantity REAL DEFAULT 0,

            harvest_date TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # --------------------------------------------------------
    # PREDICTIONS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            prediction_type TEXT NOT NULL,

            crop_name TEXT,

            predicted_value REAL,

            prediction_date TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # --------------------------------------------------------
    # TRANSACTIONS TABLE - STEP 23
    # --------------------------------------------------------

    cursor.execute("""
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

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # --------------------------------------------------------
    # PROFILE TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER UNIQUE NOT NULL,

            phone TEXT,

            location TEXT,

            village TEXT,

            district TEXT,

            state TEXT,

            land_area REAL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(name, email, password):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            password
        ))

        conn.commit()

        user_id = cursor.lastrowid

        conn.close()

        return user_id

    except sqlite3.IntegrityError:

        conn.close()

        return None


# ============================================================
# ADD USER
# Compatibility function
# ============================================================

def add_user(name, email, password):

    user_id = register_user(
        name,
        email,
        password
    )

    if user_id:

        return True

    return False


# ============================================================
# GET USER
# ============================================================

def get_user(email, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        password
    ))

    user = cursor.fetchone()

    conn.close()

    if user:

        return dict(user)

    return None


# ============================================================
# LOGIN USER
# Compatibility function
# ============================================================

def login_user(email, password):

    user = get_user(
        email,
        password
    )

    if user:

        return (
            user["id"],
            user["name"],
            user["email"]
        )

    return None


# ============================================================
# ADD CROP
# ============================================================

def add_crop(
    user_id,
    crop_name,
    planting_date,
    land_area,
    expected_harvest_date,
    water_source,
    pesticide_usage
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO crops
        (
            user_id,
            crop_name,
            planting_date,
            land_area,
            expected_harvest_date,
            water_source,
            pesticide_usage
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        crop_name,
        str(planting_date),
        land_area,
        str(expected_harvest_date),
        water_source,
        pesticide_usage
    ))

    conn.commit()

    crop_id = cursor.lastrowid

    conn.close()

    return crop_id


# ============================================================
# GET USER CROPS
# ============================================================

def get_user_crops(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            crop_name,
            planting_date,
            land_area,
            expected_harvest_date,
            water_source,
            pesticide_usage
        FROM crops
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user_id,
    ))

    crops = cursor.fetchall()

    conn.close()

    return [
        dict(crop)
        for crop in crops
    ]


# ============================================================
# GET LATEST CROP
# ============================================================

def get_latest_crop(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM crops
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        user_id,
    ))

    crop = cursor.fetchone()

    conn.close()

    if crop:

        return dict(crop)

    return None


# ============================================================
# DELETE CROP
# ============================================================

def delete_crop(crop_id, user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM crops
        WHERE id = ?
        AND user_id = ?
    """, (
        crop_id,
        user_id
    ))

    conn.commit()

    conn.close()

    return True


# ============================================================
# UPDATE CROP
# ============================================================

def update_crop(
    crop_id,
    user_id,
    crop_name,
    planting_date,
    land_area,
    expected_harvest_date,
    water_source,
    pesticide_usage
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE crops
        SET
            crop_name = ?,
            planting_date = ?,
            land_area = ?,
            expected_harvest_date = ?,
            water_source = ?,
            pesticide_usage = ?
        WHERE id = ?
        AND user_id = ?
    """, (
        crop_name,
        str(planting_date),
        land_area,
        str(expected_harvest_date),
        water_source,
        pesticide_usage,
        crop_id,
        user_id
    ))

    conn.commit()

    conn.close()

    return True


# ============================================================
# ADD CROP HISTORY
# ============================================================

def add_crop_history(
    user_id,
    crop_name,
    quantity=0,
    harvest_date=None
):

    if harvest_date is None:

        harvest_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO crop_history
        (
            user_id,
            crop_name,
            quantity,
            harvest_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        crop_name,
        quantity,
        str(harvest_date)
    ))

    conn.commit()

    history_id = cursor.lastrowid

    conn.close()

    return history_id


# ============================================================
# GET CROP HISTORY
# ============================================================

def get_crop_history(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM crop_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user_id,
    ))

    history = cursor.fetchall()

    conn.close()

    return [
        dict(item)
        for item in history
    ]


# ============================================================
# SAVE PREDICTION
# ============================================================

def save_prediction(
    user_id,
    prediction_type,
    crop_name,
    predicted_value
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions
        (
            user_id,
            prediction_type,
            crop_name,
            predicted_value,
            prediction_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        prediction_type,
        crop_name,
        predicted_value,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()

    prediction_id = cursor.lastrowid

    conn.close()

    return prediction_id


# ============================================================
# GET PREDICTIONS
# ============================================================

def get_predictions(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user_id,
    ))

    predictions = cursor.fetchall()

    conn.close()

    return [
        dict(item)
        for item in predictions
    ]


# ============================================================
# ADD TRANSACTION - STEP 23
# ============================================================

def add_transaction(
    user_id,
    crop_name,
    buyer_name,
    quantity,
    price,
    status
):

    total_amount = quantity * price

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (
            user_id,
            crop_name,
            buyer_name,
            quantity,
            price,
            total_amount,
            transaction_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        crop_name,
        buyer_name,
        quantity,
        price,
        total_amount,
        datetime.now().strftime("%Y-%m-%d"),
        status
    ))

    conn.commit()

    transaction_id = cursor.lastrowid

    conn.close()

    return transaction_id


# ============================================================
# GET TRANSACTIONS - STEP 23
# ============================================================

def get_transactions(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user_id,
    ))

    transactions = cursor.fetchall()

    conn.close()

    return [
        dict(transaction)
        for transaction in transactions
    ]


# ============================================================
# SAVE PROFILE
# ============================================================

def save_profile(
    user_id,
    phone,
    location,
    village,
    district,
    state,
    land_area
):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO profiles
        (
            user_id,
            phone,
            location,
            village,
            district,
            state,
            land_area
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            phone = excluded.phone,
            location = excluded.location,
            village = excluded.village,
            district = excluded.district,
            state = excluded.state,
            land_area = excluded.land_area
    """, (
        user_id,
        phone,
        location,
        village,
        district,
        state,
        land_area
    ))

    conn.commit()

    conn.close()

    return True


# ============================================================
# GET PROFILE
# ============================================================

def get_profile(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM profiles
        WHERE user_id = ?
    """, (
        user_id,
    ))

    profile = cursor.fetchone()

    conn.close()

    if profile:

        return dict(profile)

    return None
# ============================================================
# GET USER BY ID
# ============================================================

def get_user_by_id(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE id = ?
    """, (
        user_id,
    ))

    user = cursor.fetchone()

    conn.close()

    if user:

        return dict(user)

    return None