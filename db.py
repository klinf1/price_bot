import sqlite3


def get_connection():
    con = sqlite3.connect('../db/item_history.db', isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    return con, cur


def get_current_data(id):
    con, cur = get_connection()
    query = 'SELECT * FROM {} ORDER BY time DESC LIMIT 1'.format(f'[{id}]')
    try:
        data = cur.execute(query).fetchall()
        name = cur.execute(
            'SELECT name FROM item_list WHERE id=?',
            [id]
        ).fetchone()
    except Exception:
        con.close()
        return None, None
    con.close()
    return data[0], name


def get_id_by_name(name):
    con, cur = get_connection()
    name = str(name)
    query = "SELECT * from item_list WHERE name LIKE '%{}%'".format(name)
    data = cur.execute(query).fetchall()
    con.close()
    return data
