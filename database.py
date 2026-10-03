import sqlite3
import json
import hashlib

DB_FILE = "autoinsight.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            file_name TEXT NOT NULL,
            data_summary TEXT NOT NULL,
            executive_report TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def register_user(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email.lower(), hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = ?", (email.lower(),))
    record = c.fetchone()
    conn.close()
    if record and record[0] == hash_password(password):
        return True
    return False

def save_analysis_history(user_email: str, file_name: str, data_summary: dict, executive_report: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (user_email, file_name, data_summary, executive_report)
        VALUES (?, ?, ?, ?)
    """, (user_email.lower(), file_name, json.dumps(data_summary), executive_report))
    conn.commit()
    conn.close()

def get_user_history(user_email: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT file_name, data_summary, executive_report, created_at FROM history WHERE user_email = ? ORDER BY id DESC", (user_email.lower(),))
    rows = c.fetchall()
    conn.close()
    
    records = []
    for r in rows:
        records.append({
            "file_name": r[0],
            "data_summary": json.loads(r[1]),
            "executive_report": r[2],
            "created_at": r[3]
        })
    return records
