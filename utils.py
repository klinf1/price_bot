from datetime import datetime
import db


def check_id_list(item_id):
    con, cur = db.get_connection()
    id_list = [str(id[0]) for id in cur.execute('SELECT id FROM item_list')]
    con.close()
    if item_id not in id_list:
        return False
    return True


def get_time(input):
    dt = datetime.strptime(input, '%Y-%m-%d %H:%M:%S')
    dt = datetime.strftime(dt, '%d.%m %H:%M')
    return str(dt)
