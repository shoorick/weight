from flask import Flask, render_template, request, url_for, flash, redirect
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
app.config['SECRET_KEY'] = 'ytnnjUtdb[,n!'

@app.route('/', methods=('GET', 'POST'))
def index():
    entry_title    = request.form.get('entry_title',    '')
    category_id    = request.form.get('category_id',    '')
    category_title = request.form.get('category_title', '')

    if request.method == 'POST':
        if not entry_title:
            flash('Value is required')
        elif not category_id and not category_title:
            flash('Category must be chosen or created')
        elif category_title:
            flash('Category creation not yet implemented')
        else:
            connection = db_connect()
            connection.execute(
                'INSERT INTO entries (category_id, entry) VALUES (?, ?)',
                (category_id, entry_title)
            )
            connection.commit()
            connection.close()
            flash('Saved successfully')
            return redirect(url_for('index'))

    form = {
        entry_title:    entry_title,
        category_id:    category_id,
        category_title: category_title
    }

    connection = db_connect()
    entries = connection.execute('SELECT * FROM entries LIMIT 5').fetchall()
    connection.close()

    return render_template('index.html', form = form, entries = entries)

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

app.add_url_rule('/favicon.ico',
    redirect_to=url_for('static', filename='favicon.ico'))
