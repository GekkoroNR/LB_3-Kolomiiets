from flask import Flask, request, abort, jsonify
import sqlite3

from scipy.constants import value

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

def check_json():
    if 'Content-Type' not in request.headers:
        return abort(400)
    elif request.headers['Content-Type'] != 'application/json':
        return  abort(400)


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
        resp = 'This item doesn\'t exist'
    con.close()
    return resp

@app.route("/items", methods = ['POST'])
def add_item():
    check_json()
    print(request.json['item_name'])
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
@app.route("/items", methods = ['PUT'])
def change_item():
    check_json()
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if auth(cursor):                                                 #Авторизація
        con.close()
        return 'I don\'t know you'
    elif check_existing(cursor, 0, 'param'):           #Перевірка існування об'єкту зміни
        con.close()
        return 'This item doesn\'t in list'
    elif check_existing(cursor, 1, 'new_item_name'):   #Перевірка унікальності нового ім'я
        con.close()
        return 'This name is already in list'
    else:
        if str(request.json['param']).isdigit():                      #Пошук по ID
            cursor.execute('UPDATE Items SET item_name = ?, price = ? WHERE id = ?',
                           (request.json['new_item_name'], request.json['price'], request.json['param']))
        else:                                                         #Пошук по назві
            cursor.execute('UPDATE Items SET item_name = ?, price = ? WHERE item_name = ?',
                           (request.json['new_item_name'], request.json['price'], request.json['param']))
        con.commit()
        con.close()
        return 'Your item was changed'
@app.route("/items", methods = ['POST'])
def delite_item():
    check_json()
    print(request.json['item_name'])
    con = sqlite3.connect(catalog_name)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    if auth(cursor):
        con.close()
        return 'I don\'t know you'
    elif check_existing(cursor, 1):
        con.close()
        return 'This item is already in list'
    else:
        cursor.execute('INSERT INTO Items (item_name, price) VALUES (?, ?)',
                       (request.json['item_name'], request.json['price']))
        edit_id = cursor.lastrowid
        con.commit()
        con.close()
        return f'Your item successfully edited with ID: {edit_id}'

def auth(cursor):
    cursor.execute('SELECT * FROM Users WHERE username = ? AND password = ?',
                   (request.authorization['username'],request.authorization['password']))
    resp = list(map(dict, cursor.fetchall()))
    if len(resp) == 0:
        return True
def check_existing(cursor, existing, param):
    if param in request.json:
        if str(request.json[param]).isdigit():
            cursor.execute('SELECT COUNT(*) FROM Items WHERE id = ?',
                       (request.json[param],))
        else:
            cursor.execute('SELECT COUNT(*) FROM Items WHERE item_name = ?',
                           (request.json[param],))
        quantity = list(map(dict, cursor.fetchall()))
        if quantity[0]['COUNT(*)'] == existing:
            print(param)
            return True


if __name__ == '__main__':
    app.run(port=8000)
