from datetime import datetime
import os
import random
import string

import matplotlib
from matplotlib import pyplot as plt

import db_con
import itertools


def check_id_list(item_id):
    con, cur = db_con.get_connection()
    id_list = [str(id[0]) for id in cur.execute('SELECT id FROM item_list')]
    con.close()
    if item_id not in id_list:
        return False
    return True


def check_date(id, date):
    con, cur = db_con.get_connection()
    query = 'SELECT * FROM {} WHERE time LIKE ?'.format(f'[{id}]')
    data = cur.execute(query, ('%'+str(date)+'%', )).fetchall()
    if data:
        return True
    return False


def get_time(input):
    dt = datetime.strptime(input, '%Y-%m-%d %H:%M:%S')
    dt = datetime.strftime(dt, '%d.%m %H:%M')
    return str(dt).replace(' ', '\n')


def slice_list(source, step):
    output = list(itertools.islice(source, 0, None, step))
    return output


def get_avg(source, step, digits):
    sub_lists = [source[i:i+step] for i in range(0, len(source), step)]
    averages = [round(
        sum(sub_list) / len(sub_list), digits
    ) for sub_list in sub_lists]
    return averages


def graph(x_values, y_values, name, period, title):
    matplotlib.use('Agg')
    fig, ax = plt.subplots(figsize=(35, 18))
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.plot(x_values, y_values)
    plt.xlabel('Time', fontsize=30)
    plt.ylabel(title, fontsize=30)
    plt.title(f'{title} of {name} over {period.lower()}', fontsize=40)
    for i in range(len(x_values)):
        ax.text(x_values[i], y_values[i], y_values[i], size=20)
    plt.grid()
    if not os.path.exists('graphs'):
        os.mkdir('graphs')
    random_name = ''.join(
        random.choice(string.ascii_lowercase) for i in range(8)
    )
    filename = f'graphs/{random_name}.png'
    plt.savefig(filename, dpi=150)
    plt.close()
    return filename
