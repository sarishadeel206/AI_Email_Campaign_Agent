import sqlite3

con = sqlite3.connect("history.db")

cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    income REAL,
    spending REAL,
    email TEXT
)
""")

con.commit()
con.close()


def save_email(customer_id, income, spending, email):

    con = sqlite3.connect("history.db")

    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO history(customer_id, income, spending, email)
        VALUES(?,?,?,?)
        """,
        (customer_id, income, spending, email)
    )

    con.commit()
    con.close()


def view_history():

    con = sqlite3.connect("history.db")

    cur = con.cursor()

    cur.execute("SELECT * FROM history")

    data = cur.fetchall()

    con.close()

    return data