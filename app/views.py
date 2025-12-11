from flask import jsonify
from app import app
import datetime


@app.route('/')
def hello():
    return jsonify({"message": "Welcome to the Flask API!"})


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