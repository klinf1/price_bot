import sqlite3
import os
import random
import string

import matplotlib
import matplotlib.pyplot as plt

import utils


def get_connection():
    con = sqlite3.connect('../db/item_history.db', isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    return con, cur


def get_name(id, cur):
    name = name = cur.execute(
            'SELECT name FROM item_list WHERE id=?',
            [id]
        ).fetchone()
    return name[0]


def get_current_data(id):
    con, cur = get_connection()
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
    con, cur = get_connection()
    name = str(name)
    query = "SELECT * from item_list WHERE name LIKE '%{}%'".format(name)
    data = cur.execute(query).fetchall()
    con.close()
    return data


def get_history_graph(id, period):
    con, cur = get_connection()
    if period == 'Day':
        limit = 24
    if period == 'Week':
        limit = 168
    if period == 'Month':
        limit = 5040
    query = 'SELECT lowest_price, time FROM {} ORDER BY time DESC LIMIT {}'.format(f'[{id}]', str(limit))
    data = cur.execute(query).fetchall()
    x_values = [row[1] for row in data]
    y_values = [row[0]/10000 for row in data]
    x_values.reverse()
    y_values.reverse()
    for i in range(len(x_values)):
        x_values[i] = utils.get_time(x_values[i])
    name = get_name(id, cur)
    con.close()
    matplotlib.use('Agg')
    plt.rcParams["figure.figsize"] = (20, 20)
    plt.plot(x_values, y_values)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title(f'Price of {name} over {period.lower()}')
    if not os.path.exists('graphs'):
        os.mkdir('graphs')
    filename = f'graphs/{"".join(random.choice(string.ascii_lowercase) for i in range(8))}.png'
    plt.savefig(filename)
    plt.close()
    return filename
