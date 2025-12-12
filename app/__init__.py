import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_smorest import Api

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
api = Api()

def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__)
    
    # Configure the app
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Load environment-specific config
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        app.config.from_pyfile('config.py', silent=True)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize API
    api.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes.healthcheck import healthcheck_bp
    from app.routes.user_routes import user_bp
    from app.routes.category_routes import category_bp
    from app.routes.account_routes import account_bp
    from app.routes.expense_routes import expense_bp
    
    app.register_blueprint(healthcheck_bp)
    api.register_blueprint(user_bp)
    api.register_blueprint(category_bp)
    api.register_blueprint(account_bp)
    api.register_blueprint(expense_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.error(f'Bad Request: {error}')
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.error(f'Not Found: {error}')
        return jsonify({
            "error": "Not Found",
            "message": str(error.description) if hasattr(error, 'description') else "Resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        app.logger.error(f'Unprocessable Entity: {error}')
        messages = error.data.get('messages', {})
        if 'json' in messages:
            return jsonify({
                "error": "Validation Error",
                "message": "Invalid input data",
                "errors": messages['json']
            }), 422
        return jsonify({
            "error": "Unprocessable Entity",
            "message": str(error.description) if hasattr(error, 'description') else "Validation error"
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled Exception: {error}')
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500