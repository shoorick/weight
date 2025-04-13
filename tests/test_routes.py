import pytest
from flask import session, g
import json


def test_index_page(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Overview' in response.data
    assert b'Store new value' in response.data


def test_table_all_page(client):
    """Test that the table page with all entries loads correctly."""
    response = client.get('/table')
    assert response.status_code == 200
    assert b'All Categories Data' in response.data
    # Check for entries from test data
    assert b'75.5' in response.data
    assert b'74.8' in response.data
    assert b'180' in response.data


def test_table_category_page(client):
    """Test that the table page for a specific category loads correctly."""
    response = client.get('/table/1')
    assert response.status_code == 200
    assert b'Weight Data' in response.data
    # Check for entries from test data for Weight category
    assert b'75.5' in response.data
    assert b'74.8' in response.data
    # Height entry should not be present
    assert b'180' not in response.data


def test_graph_page(client):
    """Test that the graph page loads correctly."""
    response = client.get('/graph/1')
    assert response.status_code == 200
    assert b'Weight Graph' in response.data
    assert b'plotly-chart' in response.data
    # Check for the presence of JSON data for Plotly
    assert b'JSON.parse' in response.data


def test_add_entry_to_existing_category(client):
    """Test adding a new entry to an existing category."""
    response = client.post('/', data={
        'entry_title': '76.2',
        'category_id': '1',
        'category_title': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Saved successfully' in response.data
    
    # Check that the entry was added
    response = client.get('/table/1')
    assert b'76.2' in response.data


def test_add_entry_with_new_category(client):
    """Test adding a new entry with a new category."""
    response = client.post('/', data={
        'entry_title': '65.5',
        'category_id': '',
        'category_title': 'Blood Pressure'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Category and entry saved successfully' in response.data
    
    # Check that the new category appears in the table list
    response = client.get('/table')
    assert b'Blood Pressure' in response.data
    assert b'65.5' in response.data


def test_missing_value_validation(client):
    """Test validation when entry value is missing."""
    response = client.post('/', data={
        'entry_title': '',
        'category_id': '1',
        'category_title': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Value is required' in response.data


def test_missing_category_validation(client):
    """Test validation when no category is selected or created."""
    response = client.post('/', data={
        'entry_title': '80.0',
        'category_id': '',
        'category_title': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Category must be chosen or created' in response.data


def test_nonexistent_category(client):
    """Test accessing a category that doesn't exist."""
    response = client.get('/table/999')
    assert response.status_code == 404


def test_graph_no_data(client, app):
    """Test graph page for a category with no entries."""
    # Create a new empty category
    with app.app_context():
        import app as flask_app
        connection = flask_app.db_connect()
        cursor = connection.execute('INSERT INTO categories (title) VALUES (?)', ('Empty Category',))
        new_id = cursor.lastrowid
        connection.commit()
        connection.close()
    
    # Try to access the graph for this empty category
    response = client.get(f'/graph/{new_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'No data to display' in response.data
