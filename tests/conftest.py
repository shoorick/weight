import os
import tempfile
import pytest
import sqlite3
from app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SERVER_NAME': 'localhost',
    })
    
    # Override the db_connect function to use the test database
    def _get_db():
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        return connection
    
    # Replace the original db_connect with our test version
    import app
    app.db_connect = _get_db
    
    # Create the database and load test data
    with flask_app.app_context():
        # Initialize the database
        with open(os.path.join(os.path.dirname(__file__), '..', 'db', 'schema.sql'), 'r') as f:
            connection = _get_db()
            connection.executescript(f.read())
            
        # Add test data
        connection = _get_db()
        connection.execute('INSERT INTO categories (title) VALUES (?)', ('Weight',))
        connection.execute('INSERT INTO categories (title) VALUES (?)', ('Height',))
        connection.execute('INSERT INTO entries (category_id, entry) VALUES (?, ?)', (1, 75.5))
        connection.execute('INSERT INTO entries (category_id, entry) VALUES (?, ?)', (1, 74.8))
        connection.execute('INSERT INTO entries (category_id, entry) VALUES (?, ?)', (2, 180))
        connection.commit()
        connection.close()

    # Return the app for testing
    yield flask_app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()
