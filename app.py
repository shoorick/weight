from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
import os
import sqlite3
from werkzeug.exceptions import abort
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
import matplotlib.pyplot as plt
import io
import base64
import plotly.express as px
import plotly.utils
import json
from datetime import datetime

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

def get_categories():
    connection = db_connect()
    categories = connection.execute('SELECT * FROM categories ORDER BY title').fetchall()
    connection.close()
    return categories

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ytnnjUtdb[,n!'  # FIXME do not store in git

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
            connection = db_connect()
            cursor = connection.execute(
                'INSERT INTO categories (title) VALUES (?)',
                (category_title,)
            )
            category_id = cursor.lastrowid
            connection.execute(
                'INSERT INTO entries (category_id, entry) VALUES (?, ?)',
                (category_id, entry_title)
            )
            connection.commit()
            connection.close()
            flash('Category and entry saved successfully')
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
        'entry_title':    entry_title,
        'category_id':    category_id,
        'category_title': category_title
    }

    connection = db_connect()
    entries = connection.execute('''
        SELECT entries.*, categories.title as category_title 
        FROM entries 
        LEFT JOIN categories ON entries.category_id = categories.id 
        ORDER BY entries.created DESC 
        LIMIT 5
    ''').fetchall()
    categories = connection.execute('SELECT * FROM categories ORDER BY title').fetchall()
    
    # Get the most recently used category_id if no category is selected
    if not category_id and not category_title:
        last_entry = connection.execute(
            'SELECT category_id FROM entries ORDER BY created DESC LIMIT 1'
        ).fetchone()
        if last_entry:
            form['category_id'] = str(last_entry['category_id'])
    
    connection.close()

    return render_template('index.html', form=form, entries=entries, categories=categories, category=None)

@app.route('/table/<int:id>')
def table(id):
    # Get category info
    category = get_category(id)
    
    # Get entries for this category
    connection = db_connect()
    entries = connection.execute(
        'SELECT * FROM entries WHERE category_id = ? ORDER BY created DESC',
        (id,)
    ).fetchall()
    
    # Get all categories for navigation
    categories = connection.execute('SELECT * FROM categories').fetchall()
    connection.close()

    return render_template('table.html', entries=entries, categories=categories, category=category)

@app.route('/table')
def table_all():
    # Get all entries
    connection = db_connect()
    entries = connection.execute('''
        SELECT entries.*, categories.title as category_title
        FROM entries
        LEFT JOIN categories ON entries.category_id = categories.id
        ORDER BY entries.created DESC
    ''').fetchall()
    # Get all categories for navigation
    categories = connection.execute('SELECT * FROM categories ORDER BY title').fetchall()
    connection.close()
    return render_template('table.html', entries=entries, categories=categories, category=None)

@app.route('/table_redirect')
def table_redirect():
    return redirect(url_for('table_all'))

@app.route('/categories/<int:id>')
def category(id):
    category = get_category(id)
    return render_template('category.html', category=category)

@app.route('/graph/<int:id>')
def graph(id):
    # Get category info
    category = get_category(id)
    
    # Get entries for this category
    connection = db_connect()
    entries = connection.execute(
        'SELECT * FROM entries WHERE category_id = ? ORDER BY created ASC',
        (id,)
    ).fetchall()
    connection.close()

    if not entries:
        flash('No data to display')
        return redirect(url_for('table', id=id))

    # Prepare data for plotting
    dates = [datetime.strptime(entry['created'], '%Y-%m-%d %H:%M:%S') for entry in entries]
    values = [float(entry['entry']) for entry in entries]

    # Create an interactive plot with Plotly
    fig = px.line(
        x=dates, 
        y=values,
        title=f"{category['title']} Over Time",
        labels={'x': 'Date', 'y': 'Value'}
    )

    # Add interactive features
    fig.update_layout(
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Reset Zoom",
                        method="relayout",
                        args=[{"xaxis.range": None, "yaxis.range": None}]
                    )
                ]
            )
        ]
    )
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=2),
        marker=dict(size=8),
        hovertemplate='%{y:.1f}<br>%{x|%Y-%m-%d %H:%M}<extra></extra>'
    )

    # Convert plot to JSON for rendering in template
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'graph.html',
        plot_json=plot_json,
        category=category,
        categories=get_categories()
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')
