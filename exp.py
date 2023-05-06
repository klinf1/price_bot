import db_con
import utils
import db

def get_exact_date_graphs(id, date):
    con, cur = db_con.get_connection()
    query_price = "SELECT lowest_price, time FROM {} WHERE time LIKE ? ORDER BY time ASC".format(f'[{id}]')
    data_price = cur.execute(query_price, ('%'+str(date)+'%', )).fetchall()
    x_values_price = [row[1] for row in data_price]
    y_values_price = [round(row[0]/10000, 2) for row in data_price]
    print(y_values_price[0], type(y_values_price[0]))
    for i in range(len(x_values_price)):
        x_values_price[i] = utils.get_time(x_values_price[i])

    name = db.get_name(id, cur)
    con.close()
    file_price = utils.graph(x_values_price, y_values_price, name, date, 'Price')



def check_date(id, date):
    con, cur = db_con.get_connection()
    query = 'SELECT * FROM {} WHERE time LIKE ?'.format(f'[{id}]')
    data = cur.execute(query, ('%'+str(date)+'%', )).fetchall()
    if data:
        print('True')
    print('False')
    con.close()

check_date(117, '2000-01-01')
check_date(117, '2023-05-02')
