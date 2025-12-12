import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.account import Account
from app.models.expense import Expense
from app.models.income import Income

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Default headers for authenticated requests."""
    return {
        'Content-Type': 'application/json'
    }

def test_healthcheck(client):
    """Test healthcheck endpoint."""
    response = client.get('/healthcheck')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_create_user(client, auth_headers):
    """Test creating a new user."""
    user_data = {
        'name': 'Test User'
    }
    
    response = client.post('/api/users', 
                          data=json.dumps(user_data),
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test User'
    assert 'id' in data

def test_create_account(client, auth_headers):
    """Test creating a new account."""
    # First create a user
    user_response = client.post('/api/users',
                               data=json.dumps({'name': 'Account User'}),
                               headers=auth_headers)
    user_id = json.loads(user_response.data)['id']
    
    # Create account for user
    account_data = {
        'user_id': user_id
    }
    
    response = client.post('/api/accounts',
                          data=json.dumps(account_data),
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user_id'] == user_id
    assert data['balance'] == 0.0

def test_add_income(client, auth_headers):
    """Test adding income to account."""
    # Create user and account
    user_response = client.post('/api/users',
                               data=json.dumps({'name': 'Income User'}),
                               headers=auth_headers)
    user_id = json.loads(user_response.data)['id']
    
    # Get user's account
    accounts_response = client.get(f'/api/accounts?user_id={user_id}')
    account_id = json.loads(accounts_response.data)[0]['id']
    
    # Add income
    income_data = {
        'amount': 1000.0,
        'description': 'Salary'
    }
    
    response = client.post(f'/api/accounts/{account_id}/income',
                          data=json.dumps(income_data),
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 1000.0
    assert data['description'] == 'Salary'
    
    # Check balance updated
    balance_response = client.get(f'/api/accounts/{account_id}/balance')
    balance_data = json.loads(balance_response.data)
    assert balance_data['balance'] == 1000.0

def test_create_expense(client, auth_headers):
    """Test creating an expense with account withdrawal."""
    # Create user, account, and category
    user_response = client.post('/api/users',
                               data=json.dumps({'name': 'Expense User'}),
                               headers=auth_headers)
    user_id = json.loads(user_response.data)['id']
    
    # Get user's account
    accounts_response = client.get(f'/api/accounts?user_id={user_id}')
    account_id = json.loads(accounts_response.data)[0]['id']
    
    # Get a category
    categories_response = client.get('/api/categories')
    category_id = json.loads(categories_response.data)[0]['id']
    
    # Add income first
    income_data = {'amount': 500.0, 'description': 'Initial deposit'}
    client.post(f'/api/accounts/{account_id}/income',
                data=json.dumps(income_data),
                headers=auth_headers)
    
    # Create expense
    expense_data = {
        'user_id': user_id,
        'category_id': category_id,
        'account_id': account_id,
        'amount': 100.0,
        'description': 'Lunch'
    }
    
    response = client.post('/api/expenses',
                          data=json.dumps(expense_data),
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 100.0
    
    # Check balance after expense
    balance_response = client.get(f'/api/accounts/{account_id}/balance')
    balance_data = json.loads(balance_response.data)
    assert balance_data['balance'] == 400.0  # 500 - 100

def test_insufficient_funds(client, auth_headers):
    """Test creating expense with insufficient funds."""
    # Create user, account, and category
    user_response = client.post('/api/users',
                               data=json.dumps({'name': 'Poor User'}),
                               headers=auth_headers)
    user_id = json.loads(user_response.data)['id']
    
    # Get user's account
    accounts_response = client.get(f'/api/accounts?user_id={user_id}')
    account_id = json.loads(accounts_response.data)[0]['id']
    
    # Get a category
    categories_response = client.get('/api/categories')
    category_id = json.loads(categories_response.data)[0]['id']
    
    # Try to create expense without funds
    expense_data = {
        'user_id': user_id,
        'category_id': category_id,
        'account_id': account_id,
        'amount': 100.0
    }
    
    response = client.post('/api/expenses',
                          data=json.dumps(expense_data),
                          headers=auth_headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Insufficient funds' in data['message']

def test_validation_errors(client, auth_headers):
    """Test validation errors."""
    # Test invalid user creation
    invalid_user = {'name': ''}
    response = client.post('/api/users',
                          data=json.dumps(invalid_user),
                          headers=auth_headers)
    assert response.status_code == 422
    
    # Test invalid expense
    invalid_expense = {
        'user_id': 'invalid',
        'category_id': 'invalid',
        'account_id': 'invalid',
        'amount': -100  # Negative amount
    }
    response = client.post('/api/expenses',
                          data=json.dumps(invalid_expense),
                          headers=auth_headers)
    assert response.status_code == 422