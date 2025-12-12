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
            "status": "healthy",
            "version": "2.0.0"
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
        "docs": "/swagger-ui",
        "auth_required": "Most endpoints require JWT authentication",
        "auth_endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "refresh": "POST /api/auth/refresh",
            "profile": "GET /api/auth/me"
        }
    }), 200

@healthcheck_bp.route('/status', methods=['GET'])
def status():
    """Detailed status endpoint."""
    try:
        from app import db
        from sqlalchemy import text
        
        # Check database connection
        db_status = "connected"
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": db_status,
            "services": {
                "api": "running",
                "authentication": "enabled",
                "documentation": "available at /swagger-ui"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }), 500