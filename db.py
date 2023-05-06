import db_con
import utils


def get_name(id, cur):
    name = name = cur.execute(
            'SELECT name FROM item_list WHERE id=?',
            [id]
        ).fetchone()
    return name[0]


def get_current_data(id):
    con, cur = db_con.get_connection()
    query = 'SELECT * FROM {} ORDER BY time DESC LIMIT 1'.format(f'[{id}]')
    try:
        data = cur.execute(query).fetchall()
        name = get_name(id, cur)
    except Exception:
        con.close()
        return None, None
    con.close()
    return data[0], name


def get_id_by_name(name):
    con, cur = db_con.get_connection()
    name = str(name)
    query = "SELECT * from item_list WHERE name LIKE '%{}%'".format(name)
    data = cur.execute(query).fetchall()
    con.close()
    return data


def get_history_graph(id, period):
    con, cur = db_con.get_connection()
    if period == 'One day':
        limit = 24
        step = 1
    if period == '7 days':
        limit = 168
        step = 4
    if period == '30 days':
        limit = 5040
        step = 15
    query_price = 'SELECT lowest_price, time FROM {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    query_amount = 'SELECT amount_on_sale, time FROM {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    query_sellers = 'SELECT sellers, time from {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    data_price = cur.execute(query_price).fetchall()
    data_amount = cur.execute(query_amount).fetchall()
    data_sellers = cur.execute(query_sellers).fetchall()
    x_values_price = [row[1] for row in data_price]
    y_values_price = [round(row[0]/10000, 2) for row in data_price]
    x_values_amount = x_values_price
    y_values_amount = [round(row[0], 0) for row in data_amount]
    x_values_sellers = x_values_price
    y_values_sellers = [round(row[0], 0) for row in data_sellers]
    for i in range(len(x_values_price)):
        x_values_price[i] = utils.get_time(x_values_price[i])
    name = get_name(id, cur)
    x_values_price = utils.slice_list(x_values_price, step)
    y_values_price = utils.get_avg(y_values_price, step)
    y_values_amount = utils.get_avg(y_values_amount, step)
    y_values_sellers = utils.get_avg(y_values_sellers, step)
    x_values_price.reverse()
    y_values_price .reverse()
    y_values_amount.reverse()
    y_values_sellers.reverse()
    x_values_sellers = x_values_price
    x_values_amount = x_values_price
    con.close()
    file_price = utils.graph(x_values_price, y_values_price, name, period, 'Price')
    file_amount = utils.graph(x_values_amount, y_values_amount, name, period, 'Amount on sale')
    file_sellers = utils.graph(x_values_sellers, y_values_sellers, name, period, 'Sellers')
    return file_price, file_amount, file_sellers


def get_subs(chat_id):
    con, cur = db_con.get_connection()
    cur.execute('CREATE TABLE if NOT EXISTS user_subs (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id NOT NULL, item_id NOT NULL)')
    con.commit()
    tuples = cur.execute('SELECT item_id FROM user_subs WHERE chat_id=?', [chat_id, ]).fetchall()
    sub_ids = [id[0] for id in tuples]
    con.close()
    return sub_ids


def add_sub(chat_id, item_id):
    con, cur = db_con.get_connection()
    cur.execute('CREATE TABLE if NOT EXISTS user_subs (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id NOT NULL, item_id NOT NULL)')
    cur.execute('INSERT INTO user_subs (chat_id, item_id) VALUES (?,?)', [chat_id, item_id])
    con.commit()
    con.close()


def delete_sub(chat_id, item_id):
    con, cur = db_con.get_connection()
    cur.execute('DELETE from user_subs WHERE chat_id=? AND item_id=?', [chat_id, item_id])
    con.commit()
    con.close()


def list_subs(chat_id):
    sub_ids = get_subs(chat_id)
    to_return = []
    con, cur = db_con.get_connection()
    for id in sub_ids:
        info = cur.execute('SELECT * from item_list WHERE id=?', [id, ]).fetchone()
        to_return.append(info)
    con.close()
    return to_return
