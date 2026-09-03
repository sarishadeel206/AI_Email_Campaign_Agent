import sqlite3


def _get_connection():
    return sqlite3.connect("history.db")


def init_db():
    """Create the history table if it does not exist."""
    con = _get_connection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            income REAL,
            spending REAL,
            segment TEXT,
            subject TEXT,
            email TEXT,
            generated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # Add missing columns to existing databases (migration safety)
    existing_cols = {row[1] for row in cur.execute("PRAGMA table_info(history)")}
    if "segment" not in existing_cols:
        cur.execute("ALTER TABLE history ADD COLUMN segment TEXT")
    if "subject" not in existing_cols:
        cur.execute("ALTER TABLE history ADD COLUMN subject TEXT")
    if "generated_at" not in existing_cols:
        cur.execute("ALTER TABLE history ADD COLUMN generated_at TEXT")
        cur.execute("UPDATE history SET generated_at = datetime('now') WHERE generated_at IS NULL")
    con.commit()
    con.close()


def save_email(customer_id, income, spending, segment, subject, email):
    con = _get_connection()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO history(customer_id, income, spending, segment, subject, email, generated_at)
        VALUES(?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (customer_id, income, spending, segment, subject, email)
    )
    con.commit()
    con.close()


def view_history():
    con = _get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT id, customer_id, income, spending, segment, subject, email, generated_at FROM history ORDER BY id DESC"
    )
    data = cur.fetchall()
    con.close()
    return data
