import pytest
from app import get_category, get_categories, db_connect


def test_db_connect(app):
    """Test database connection function."""
    with app.app_context():
        connection = db_connect()
        assert connection is not None
        
        # Test that we can execute a query
        cursor = connection.execute('SELECT 1')
        result = cursor.fetchone()
        assert result[0] == 1
        
        connection.close()


def test_get_category_existing(app):
    """Test retrieving an existing category."""
    with app.app_context():
        # Get the Weight category (id=1 from test data)
        category = get_category(1)
        assert category is not None
        assert category['id'] == 1
        assert category['title'] == 'Weight'


def test_get_category_nonexistent(app):
    """Test retrieving a non-existent category."""
    with app.app_context():
        # Try to get a category that doesn't exist
        with pytest.raises(Exception) as excinfo:
            get_category(999)
        # Check that a 404 error is raised
        assert '404' in str(excinfo.value)


def test_get_categories(app):
    """Test retrieving all categories."""
    with app.app_context():
        categories = get_categories()
        
        # Check that we have at least the two categories from test data
        assert len(categories) >= 2
        
        # Check that the categories are sorted by title
        category_titles = [category['title'] for category in categories]
        sorted_titles = sorted(category_titles)
        assert category_titles == sorted_titles
        
        # Check that our test categories are present
        titles = set(category_titles)
        assert 'Weight' in titles
        assert 'Height' in titles
