import sqlite3
from flask import g

DB_NAME = 'log.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            host_name TEXT,
            host_ip TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_log(timestamp, name, ip, status):
    db = get_db()
    db.execute('''
        INSERT INTO logs (timestamp, host_name, host_ip, status)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, name, ip, status))
    db.commit()

def get_all_logs():
    db = get_db()
    cursor = db.execute('''
        SELECT timestamp, host_name, host_ip, status
        FROM logs
        ORDER BY id DESC
        LIMIT 100
    ''')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
