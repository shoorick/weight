from flask import Flask, render_template
import sqlite3

def db_connect():
    connection = sqlite3.connect('db/database.db')
    connection.row_factory = sqlite3.Row
    return connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table')
def table():
    connection = db_connect()
    entries = connection.execute('SELECT * FROM entries').fetchall()
    connection.close()
    return render_template('table.html', entries=entries)
