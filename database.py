import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS prompt (id INTEGER PRIMARY KEY, text TEXT)")
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users")
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users

def save_prompt(text):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM prompt")
    cur.execute("INSERT INTO prompt (id, text) VALUES (1, ?)", (text,))
    conn.commit()
    conn.close()

def get_prompt():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT text FROM prompt WHERE id = 1")
    result = cur.fetchone()
    conn.close()
    return result[0] if result else "You are a helpful assistant."