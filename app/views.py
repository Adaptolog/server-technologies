from flask import jsonify, request
from app import app
import datetime
from app.models import data_store
from app.utils import (
    get_current_timestamp, 
    validate_user_data, 
    validate_category_data, 
    validate_record_data
)

@app.route('/')
def hello():
    return jsonify({"message": "Welcome to the Expense Tracking API!"})


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Healthcheck endpoint"""
    try:
        current_time = datetime.datetime.utcnow().isoformat() + "Z"
        response = {
            "date": current_time,
            "status": "healthy"
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            "date": datetime.datetime.utcnow().isoformat() + "Z",
            "status": "error",
            "error": str(e)
        }), 500


# User endpoints
@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = data_store.get_user(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user by ID"""
    if data_store.delete_user(user_id):
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/user', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    error = validate_user_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    name = data['name'].strip()
    user = data_store.add_user(name)
    return jsonify(user.to_dict()), 201


@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    users = data_store.get_all_users()
    return jsonify([user.to_dict() for user in users]), 200

# Category endpoints
@app.route('/category', methods=['POST'])
def create_category():
    """Create a new category"""
    data = request.get_json()
    
    error = validate_category_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    name = data['name'].strip()
    category = data_store.add_category(name)
    return jsonify(category.to_dict()), 201


@app.route('/category', methods=['POST'])
def create_category():
    """Create a new category"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400
    
    category = data_store.add_category(name)
    return jsonify(category.to_dict()), 201


@app.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete category by ID"""
    if data_store.delete_category(category_id):
        return jsonify({"message": "Category deleted successfully"}), 200
    return jsonify({"error": "Category not found"}), 404

# Expense record endpoints
@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    """Get record by ID"""
    record = data_store.get_record(record_id)
    if record:
        return jsonify(record.to_dict()), 200
    return jsonify({"error": "Record not found"}), 404


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete record by ID"""
    if data_store.delete_record(record_id):
        return jsonify({"message": "Record deleted successfully"}), 200
    return jsonify({"error": "Record not found"}), 404


@app.route('/record', methods=['POST'])
def create_record():
    """Create a new expense record"""
    data = request.get_json()
    
    error = validate_record_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    user_id = data['user_id'].strip()
    category_id = data['category_id'].strip()
    amount = float(data['amount'])
    
    record = data_store.add_record(user_id, category_id, amount)
    if record:
        return jsonify(record.to_dict()), 201
    else:
        return jsonify({"error": "User or category not found"}), 404

@app.route('/record', methods=['GET'])
def get_records():
    """Get records with optional user_id and category_id filters"""
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')
    
    # At least one filter must be provided
    if user_id is None and category_id is None:
        return jsonify({"error": "At least one filter (user_id or category_id) is required"}), 400
    
    records = data_store.get_all_records(user_id, category_id)
    return jsonify([record.to_dict() for record in records]), 200