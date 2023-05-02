import sqlite3


def get_connection():
    con = sqlite3.connect('../db/item_history.db', isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    return con, cur
