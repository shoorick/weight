from flask import Flask, render_template
import sqlite3
from werkzeug.exceptions import abort

def db_connect():
    connection = sqlite3.connect('db/database.db')
    connection.row_factory = sqlite3.Row
    return connection

def get_category(id):
    connection = db_connect()
    category = connection.execute(
        'SELECT * FROM categories WHERE id = ?',
        (id,)
    ).fetchone()
    connection.close()
    if category is None:
        abort(404)
    return category

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

@app.route('/categories/<int:id>')
def category(id):
    category = get_category(id)
    return render_template('category.html', category=category)
