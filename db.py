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
    if period == 'Day':
        limit = 24
        step = 1
    if period == 'Week':
        limit = 168
        step = 4
    if period == 'Month':
        limit = 5040
        step = 15
    query_price = 'SELECT lowest_price, time FROM {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    query_amount = 'SELECT amount_on_sale, time FROM {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    data_price = cur.execute(query_price).fetchall()
    data_amount = cur.execute(query_amount).fetchall()
    x_values_price = [row[1] for row in data_price]
    y_values_price = [row[0]/10000 for row in data_price]
    x_values_amount = [row[1] for row in data_amount]
    y_values_amount = [row[0] for row in data_amount]
    for i in range(len(x_values_price)):
        x_values_price[i] = utils.get_time(x_values_price[i])
        x_values_amount[i] = utils.get_time(x_values_amount[i])
    name = get_name(id, cur)
    x_values_price = utils.slice_list(x_values_price, step)
    x_values_amount = utils.slice_list(x_values_amount, step)
    y_values_price = utils.get_avg(y_values_price, step)
    y_values_amount = utils.get_avg(y_values_amount, step)
    x_values_price.reverse()
    y_values_price .reverse()
    x_values_amount.reverse()
    y_values_amount.reverse()
    con.close()
    file_price = utils.graph(x_values_price, y_values_price, name, period, 'Price')
    file_amount = utils.graph(x_values_amount, y_values_amount, name, period, 'Amount on sale')
    return file_price, file_amount
