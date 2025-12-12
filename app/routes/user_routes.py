from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app import db
from app.models.user import User
from app.schemas.user_schema import UserSchema, UserQuerySchema

user_bp = Blueprint('users', __name__, url_prefix='/api/users', description='Operations on users')

@user_bp.route('/')
class Users(MethodView):
    @user_bp.arguments(UserQuerySchema, location='query')
    @user_bp.response(200, UserSchema(many=True))
    def get(self, args):
        """Get all users with optional filters."""
        query = User.query
        
        if 'name' in args:
            query = query.filter(User.name.ilike(f"%{args['name']}%"))
        
        users = query.order_by(User.created_at.desc()).all()
        return users
    
    @user_bp.arguments(UserSchema)
    @user_bp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user."""
        try:
            # Check if user with same name exists
            existing_user = User.query.filter_by(name=user_data['name']).first()
            if existing_user:
                abort(400, message="User with this name already exists")
            
            # Створюємо користувача
            user = User(name=user_data['name'])
            db.session.add(user)
            
            # Зберігаємо користувача, щоб отримати його ID
            db.session.flush()  # Flush, щоб отримати ID без коміту
            
            # Create default account for user (тепер user.id вже існує)
            from app.models.account import Account
            account = Account(user_id=user.id)
            db.session.add(account)
            
            # Create default categories for user (if they don't exist)
            from app.models.category import Category
            default_categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping']
            for category_name in default_categories:
                existing_category = Category.query.filter_by(
                    name=category_name, 
                    is_global=True
                ).first()
                if not existing_category:
                    category = Category(name=category_name, is_global=True)
                    db.session.add(category)
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {str(e)}")
            abort(500, message=f"Failed to create user: {str(e)}")

@user_bp.route('/<user_id>')
class UserById(MethodView):
    @user_bp.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID."""
        user = User.query.get_or_404(user_id)
        return user
    
    @user_bp.arguments(UserSchema)
    @user_bp.response(200, UserSchema)
    def put(self, user_data, user_id):
        """Update user by ID."""
        try:
            user = User.query.get_or_404(user_id)
            
            # Check if name is being changed and if it conflicts
            if 'name' in user_data and user_data['name'] != user.name:
                existing_user = User.query.filter_by(name=user_data['name']).first()
                if existing_user and existing_user.id != user_id:
                    abort(400, message="User with this name already exists")
            
            user.name = user_data['name']
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Failed to update user: {str(e)}")
    
    @user_bp.response(204)
    def delete(self, user_id):
        """Delete user by ID."""
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Failed to delete user: {str(e)}")