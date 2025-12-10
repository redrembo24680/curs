"""Unit tests for Flask application."""
from app import create_app
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestFlaskApp(unittest.TestCase):
    """Test Flask application."""

    def setUp(self):
        """Set up test client."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_home_page(self):
        """Test home page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        """Test login page loads."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        """Test register page loads."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)


class TestAuthentication(unittest.TestCase):
    """Test authentication routes."""

    def setUp(self):
        """Set up test client."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_user_info_endpoint(self):
        """Test user info endpoint."""
        response = self.client.get('/api/user-info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('logged_in', data)

    def test_flask_stats_endpoint(self):
        """Test Flask stats endpoint."""
        response = self.client.get('/api/flask-stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('total_votes', data)


if __name__ == '__main__':
    unittest.main()
