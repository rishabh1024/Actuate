# database.py
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL UNIQUE,
            short_url TEXT NOT NULL UNIQUE,
            expiry_date TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

"""
get_url_by_short_url: Fetches a URL from the database by its short URL.
params: short_url: str
returns: url: sqlite3.Row
"""
def get_url_by_short_url(short_url: str):

    conn = get_db_connection()
    url = conn.execute(
        'SELECT * FROM urls WHERE short_url = ?', (short_url,)
    ).fetchone()
    conn.close()
    return url


def get_url_by_original_url(original_url: str):
    conn = get_db_connection()
    url = conn.execute(
        'SELECT * FROM urls WHERE original_url = ?', (original_url,)
    ).fetchone()
    conn.close()
    return url


def insert_url(original_url: str, short_url: str, expiry_date: str):
    conn = get_db_connection()
    conn.execute(
        '''
        INSERT INTO urls (original_url, short_url, expiry_date, clicks)
          VALUES (?, ?, ?, ?)''',
        (original_url, short_url, expiry_date, 0)
    )
    conn.commit()
    conn.close()


def update_clicks(short_url: str):
    conn = get_db_connection()
    conn.execute(
        'UPDATE urls SET clicks = clicks + 1 WHERE short_url = ?', (short_url,)
    )
    conn.commit()
    conn.close()


create_tables()
