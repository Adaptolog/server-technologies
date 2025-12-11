import unittest
import json
from app import app


class HealthcheckTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_healthcheck_status_code(self):
        """Test healthcheck endpoint returns 200"""
        response = self.app.get('/healthcheck')
        self.assertEqual(response.status_code, 200)

    def test_healthcheck_content_type(self):
        """Test healthcheck returns JSON"""
        response = self.app.get('/healthcheck')
        self.assertEqual(response.content_type, 'application/json')

    def test_healthcheck_data_structure(self):
        """Test healthcheck response structure"""
        response = self.app.get('/healthcheck')
        data = json.loads(response.data)
        
        self.assertIn('date', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        
        # Check date format (should end with Z for UTC)
        self.assertTrue(data['date'].endswith('Z'))

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)


if __name__ == '__main__':
    unittest.main()