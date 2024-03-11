import sqlite3


def create_db():
    conn = sqlite3.connect('mqtt_messages.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mqtt_logs (
            id INTEGER PRIMARY KEY,
            topic TEXT,
            payload TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def fetch_logs():
    conn = sqlite3.connect('mqtt_messages.db')
    c = conn.cursor()
    c.execute('SELECT * FROM mqtt_logs ORDER BY timestamp DESC')
    logs = c.fetchall()
    conn.close()
    return logs


if __name__ == "__main__":
    create_db()
