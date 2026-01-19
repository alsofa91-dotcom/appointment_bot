import sqlite3

DB_NAME = "db.sqlite3"


# ---------------------------
# Инициализация базы
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # таблица для записей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        client_name TEXT,
        service_name TEXT,
        master_name TEXT,
        date TEXT,
        time TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    # таблица для услуг
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        duration INTEGER
    )
    """)

    # таблица для мастеров
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# Добавление записи
# ---------------------------
def add_booking(client_id, client_name, service_name, master_name, date, time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings (client_id, client_name, service_name, master_name, date, time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, client_name, service_name, master_name, date, time))

    conn.commit()
    conn.close()


# ---------------------------
# Получение записей по дате
# ---------------------------
def get_bookings_by_date(date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT time, service_name, master_name, client_name
    FROM bookings
    WHERE date = ? AND status='active'
    ORDER BY time
    """, (date_str,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------------------
# Получение записей между датами
# ---------------------------
def get_bookings_between(start, end):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, time, service_name, master_name, client_name
    FROM bookings
    WHERE date BETWEEN ? AND ? AND status='active'
    ORDER BY date, time
    """, (start, end))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------------------
# Сервисы
# ---------------------------
def add_service(name, duration):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (name, duration) VALUES (?, ?)", (name, duration))
    conn.commit()
    conn.close()


def get_services():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, duration FROM services")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_service_by_id(service_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM services WHERE id=?", (service_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def update_service(service_id, name, duration):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE services SET name=?, duration=? WHERE id=?", (name, duration, service_id))
    conn.commit()
    conn.close()


def delete_service(service_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services WHERE id=?", (service_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Мастера
# ---------------------------
def add_master(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO masters (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def get_masters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM masters")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_master_by_id(master_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM masters WHERE id=?", (master_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def update_master(master_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE masters SET name=? WHERE id=?", (name, master_id))
    conn.commit()
    conn.close()


def delete_master(master_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM masters WHERE id=?", (master_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Все записи (для админки)
# ---------------------------
def get_all_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, client_id, service_name, master_name, date, time
    FROM bookings
    ORDER BY date, time
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
