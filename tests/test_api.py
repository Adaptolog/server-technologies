import unittest
import json
from app import app
from app.models import data_store


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear and reinitialize data
        data_store.users.clear()
        data_store.categories.clear()
        data_store.records.clear()
        
        # Add sample data
        self.user1 = data_store.add_user("Test User 1")
        self.user2 = data_store.add_user("Test User 2")
        self.category1 = data_store.add_category("Test Category 1")
        self.category2 = data_store.add_category("Test Category 2")
        self.record1 = data_store.add_record(self.user1.id, self.category1.id, 100.0)
        self.record2 = data_store.add_record(self.user2.id, self.category2.id, 200.0)
    
    def test_healthcheck(self):
        """Test healthcheck endpoint"""
        response = self.app.get('/healthcheck')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('date', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    # User endpoint tests
    def test_get_user(self):
        """Test get user by ID"""
        response = self.app.get(f'/user/{self.user1.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test User 1')
    
    def test_get_nonexistent_user(self):
        """Test get nonexistent user"""
        response = self.app.get('/user/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_create_user(self):
        """Test create new user"""
        new_user = {'name': 'New Test User'}
        response = self.app.post('/user', 
                                data=json.dumps(new_user),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Test User')
        self.assertIn('id', data)
    
    def test_create_user_invalid_data(self):
        """Test create user with invalid data"""
        # Missing name
        response = self.app.post('/user',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Empty name
        response = self.app.post('/user',
                                data=json.dumps({'name': ''}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_users(self):
        """Test get all users"""
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 2)
    
    def test_delete_user(self):
        """Test delete user"""
        response = self.app.delete(f'/user/{self.user1.id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify user is deleted
        response = self.app.get(f'/user/{self.user1.id}')
        self.assertEqual(response.status_code, 404)
    
    # Category endpoint tests
    def test_get_all_categories(self):
        """Test get all categories"""
        response = self.app.get('/category')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data), 2)
    
    def test_create_category(self):
        """Test create new category"""
        new_category = {'name': 'New Category'}
        response = self.app.post('/category',
                                data=json.dumps(new_category),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Category')
    
    def test_delete_category(self):
        """Test delete category"""
        response = self.app.delete(f'/category/{self.category1.id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify category is deleted
        response = self.app.get(f'/category')
        data = json.loads(response.data)
        category_ids = [cat['id'] for cat in data]
        self.assertNotIn(self.category1.id, category_ids)
    
    # Record endpoint tests
    def test_get_record(self):
        """Test get record by ID"""
        response = self.app.get(f'/record/{self.record1.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['amount'], 100.0)
        self.assertEqual(data['user_id'], self.user1.id)
    
    def test_create_record(self):
        """Test create new record"""
        new_record = {
            'user_id': self.user1.id,
            'category_id': self.category1.id,
            'amount': 150.0
        }
        response = self.app.post('/record',
                                data=json.dumps(new_record),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['amount'], 150.0)
    
    def test_create_record_invalid_data(self):
        """Test create record with invalid data"""
        # Missing required fields
        response = self.app.post('/record',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Invalid user/category
        invalid_record = {
            'user_id': 'invalid',
            'category_id': 'invalid',
            'amount': 100.0
        }
        response = self.app.post('/record',
                                data=json.dumps(invalid_record),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_record(self):
        """Test delete record"""
        response = self.app.delete(f'/record/{self.record1.id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify record is deleted
        response = self.app.get(f'/record/{self.record1.id}')
        self.assertEqual(response.status_code, 404)
    
    def test_get_records_with_filters(self):
        """Test get records with filters"""
        # Filter by user_id
        response = self.app.get(f'/record?user_id={self.user1.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_id'], self.user1.id)
        
        # Filter by category_id
        response = self.app.get(f'/record?category_id={self.category2.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['category_id'], self.category2.id)
        
        # Filter by both
        response = self.app.get(f'/record?user_id={self.user1.id}&category_id={self.category1.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        
        # No filters (should error)
        response = self.app.get('/record')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()