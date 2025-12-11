from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize data store with some sample data
from app.models import data_store
def init_sample_data():
    """Initialize sample data for testing"""
    if not data_store.users:
        user1 = data_store.add_user("John Doe")
        user2 = data_store.add_user("Jane Smith")
        
        cat1 = data_store.add_category("Food")
        cat2 = data_store.add_category("Transportation")
        cat3 = data_store.add_category("Entertainment")
        
        data_store.add_record(user1.id, cat1.id, 25.50)
        data_store.add_record(user1.id, cat2.id, 15.00)
        data_store.add_record(user2.id, cat3.id, 50.00)

init_sample_data()

from app import views