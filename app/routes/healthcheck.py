from flask import Blueprint, jsonify
from datetime import datetime

healthcheck_bp = Blueprint('healthcheck', __name__)

@healthcheck_bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Healthcheck endpoint."""
    try:
        current_time = datetime.utcnow().isoformat() + "Z"
        response = {
            "date": current_time,
            "status": "healthy"
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            "date": datetime.utcnow().isoformat() + "Z",
            "status": "error",
            "error": str(e)
        }), 500

@healthcheck_bp.route('/', methods=['GET'])
def hello():
    """Root endpoint."""
    return jsonify({
        "message": "Welcome to the Expense Tracking API with Income Management!",
        "version": "2.0.0",
        "docs": "/swagger-ui"
    }), 200