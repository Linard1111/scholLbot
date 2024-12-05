import sqlite3
from datetime import datetime, timedelta

def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    """Создает таблицы в базе данных."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            duration_days INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            class TEXT,
            class_letter TEXT
        )
    ''')
    conn.commit()

def add_event(conn, name, duration_days):
    cursor = conn.cursor()
    expiration_date = datetime.now() + timedelta(days=duration_days)
    cursor.execute('INSERT INTO events (name, date, duration_days) VALUES (?, ?, ?)', (name, expiration_date.strftime('%Y-%m-%d'), duration_days))
    conn.commit()
    
def get_class_count(conn, class_name, class_letter):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE class = ? AND class_letter = ?", (class_name, class_letter))
    count = cursor.fetchone()[0]
    return count

def delete_event(conn, event_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()

def get_events(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events')
    return cursor.fetchall()

def remove_expired_events(conn):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE date < ?', (datetime.now().strftime('%Y-%m-%d'),))
    conn.commit()

def add_user(conn, user_id, username):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()

def get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()

def update_user_class(conn, user_id, class_name, class_letter):
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET class = ?, class_letter = ? WHERE id = ?', (class_name, class_letter, user_id))
    conn.commit()

if __name__ == "__main__":
    # Создаем соединение с базой данных
    conn = create_connection("bot_database.db")
    
    # Создаем таблицы
    create_table(conn)
    
    # Закрываем соединение
    conn.close()
