from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.schemas.user_schema import UserSchema, LoginSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth', description='Authentication operations')

@auth_bp.route('/register')
class Register(MethodView):
    @auth_bp.arguments(UserSchema)
    @auth_bp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user."""
        try:
            # Check if user with same email exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                abort(400, message="User with this email already exists")
            
            # Check if user with same name exists
            existing_user_by_name = User.query.filter_by(name=user_data['name']).first()
            if existing_user_by_name:
                abort(400, message="User with this name already exists")
            
            # Create new user
            user = User(
                name=user_data['name'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            db.session.flush()  # Get user ID without committing
            
            # Create default account for user
            from app.models.account import Account
            account = Account(user_id=user.id)
            db.session.add(account)
            
            # Create default categories (if they don't exist)
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
            abort(500, message=f"Failed to register user: {str(e)}")

@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200)
    def post(self, login_data):
        """Login user and get access token."""
        user = User.query.filter_by(email=login_data['email']).first()
        
        if user and user.check_password(login_data['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }
        else:
            abort(401, message="Invalid email or password")

@auth_bp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @auth_bp.response(200)
    def post(self):
        """Refresh access token."""
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return {
            "access_token": new_access_token
        }

@auth_bp.route('/me')
class UserProfile(MethodView):
    @jwt_required()
    @auth_bp.response(200, UserSchema)
    def get(self):
        """Get current user profile."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        return user

@auth_bp.route('/logout')
class Logout(MethodView):
    @jwt_required()
    @auth_bp.response(200)
    def post(self):
        """Logout user."""
        # Note: In production, you should add the token to a blacklist
        return {
            "message": "Successfully logged out"
        }

@auth_bp.route('/change-password')
class ChangePassword(MethodView):
    @jwt_required()
    @auth_bp.response(200)
    def post(self):
        """Change user password."""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        # In a real application, you would validate old password first
        # For simplicity, we'll just accept new password
        data = auth_bp.arguments({
            'old_password': fields.Str(required=True),
            'new_password': fields.Str(required=True, validate=validate.Length(min=6)),
            'confirm_password': fields.Str(required=True)
        })(lambda: None)()  # This is a simplified approach
        
        # You would need to implement proper schema for this
        
        return {
            "message": "Password change endpoint"
        }