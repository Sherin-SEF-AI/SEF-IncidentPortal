import sqlite3

DATABASE = 'security_incidents.db'

def create_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                description TEXT NOT NULL,
                date_time TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                reporter TEXT NOT NULL,
                attachment TEXT
            )
        ''')
        conn.commit()

def insert_incident(incident_data):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO incidents (incident_type, description, date_time, severity, status, reporter, attachment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', incident_data)
        conn.commit()

def get_all_incidents():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM incidents')
        return cursor.fetchall()

def register_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (username, password))
        conn.commit()

def authenticate_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return row is not None and row[0] == password

def get_incident_stats():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT severity, COUNT(*) FROM incidents GROUP BY severity
        ''')
        stats = cursor.fetchall()
        return '\n'.join([f"Severity: {row[0]}, Count: {row[1]}" for row in stats])

create_table()
