from flask import Flask, request, abort
import sqlite3

app = Flask(__name__)
catalog_name = 'global_catalog.db'

con = sqlite3.connect(catalog_name)
cursor = con.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL)''')
con.commit()
con.close()

@app.route("/")
def say_hello():
    return '<h1>First page and nothing more</h1>'


@app.route("/item/<param>", methods = ['GET'])
def get_item(param):
    check_json()
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if param.isdigit():                                           #Пошук по ID
        cursor.execute('SELECT * FROM Items WHERE id = ?', (param,))
    elif param == 'ALL_ITEMS':                                    #Пошук усіх речей
        cursor.execute('SELECT * FROM Items')
    else:                                                         #Пошук по назві
        cursor.execute('SELECT * FROM Items WHERE item_name = ?', (param,))
    resp = list(map(dict, cursor.fetchall()))
    if len(resp) == 0:
        resp = 'This item doesn\'t in list'
    con.close()
    return resp

@app.route("/items", methods = ['POST'])
def add_item():
    check_json()
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if auth(cursor):
        con.close()
        return 'I don\'t know you'
    elif check_existing(cursor, 1, 'item_name'):
        con.close()
        return 'This item is already in list'
    else:
        cursor.execute('INSERT INTO Items (item_name, price) VALUES (?, ?)',
                       (request.json['item_name'], request.json['price']))
        edit_id = cursor.lastrowid
        con.commit()
        con.close()
        return f'Your item successfully edited with ID: {edit_id}'
@app.route("/item/<param>", methods = ['PUT'])
def change_item(param):
    check_json()
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if auth(cursor):                                                 #Авторизація
        con.close()
        return 'I don\'t know you'
    elif check_existing(cursor, 0, param):           #Перевірка існування об'єкту зміни
        con.close()
        return 'This item doesn\'t in list'
    elif check_existing(cursor, 1, 'item_name'):   #Перевірка унікальності нового ім'я
        con.close()
        return 'This name is already in list'
    else:
        if param.isdigit():                      #Пошук по ID
            cursor.execute('UPDATE Items SET item_name = ?, price = ? WHERE id = ?',
                           (request.json['item_name'], request.json['price'], param))
        else:                                                         #Пошук по назві
            cursor.execute('UPDATE Items SET item_name = ?, price = ? WHERE item_name = ?',
                           (request.json['item_name'], request.json['price'], param))
        con.commit()
        con.close()
        return 'Your item was changed'
@app.route("/item/<param>", methods = ['DELETE'])
def delete_item(param):
    check_json()
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if auth(cursor):
        con.close()
        return 'I don\'t know you'
    elif check_existing(cursor, 0, param):
        con.close()
        return 'This item doesn\'t in list'
    if param.isdigit():                                          # Пошук по ID
        cursor.execute('DELETE FROM Items WHERE id = ?', (param,))
    else:                                                        # Пошук по назві
        cursor.execute('DELETE FROM Items WHERE item_name = ?', (param,))
    con.commit()
    con.close()
    return 'Item was deleted'

def check_json():
    if 'Content-Type' not in request.headers:
        return abort(400)
    elif request.headers['Content-Type'] != 'application/json':
        return  abort(400)
def auth(cursor):
    cursor.execute('SELECT * FROM Users WHERE username = ? AND password = ?',
                   (request.authorization['username'],request.authorization['password']))
    resp = list(map(dict, cursor.fetchall()))
    if len(resp) == 0:
        return True
def check_existing(cursor, existing, param):
    if request.method == 'DELETE':
        identity = param
    elif param in request.json:
        identity = request.json[param]
    else:
        identity = param
    if str(identity).isdigit():
         cursor.execute('SELECT COUNT(*) FROM Items WHERE id = ?',
                    (identity,))
    else:
        cursor.execute('SELECT COUNT(*) FROM Items WHERE item_name = ?',
                        (identity,))
    quantity = list(map(dict, cursor.fetchall()))
    if quantity[0]['COUNT(*)'] == existing:
        return True


if __name__ == '__main__':
    app.run(port=8000)
