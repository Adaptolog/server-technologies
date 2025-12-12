from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import fields, validate
from app import db
from app.models.user import User
from app.schemas.user_schema import UserSchema, UserQuerySchema

user_bp = Blueprint('users', __name__, url_prefix='/api/users', description='Operations on users')

@user_bp.route('/')
class Users(MethodView):
    @jwt_required()
    @user_bp.arguments(UserQuerySchema, location='query')
    @user_bp.response(200, UserSchema(many=True))
    def get(self, args):
        """Get all users with optional filters."""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # For security, you might want to restrict this to admins only
        # For now, allow all authenticated users
        query = User.query
        
        if 'name' in args:
            query = query.filter(User.name.ilike(f"%{args['name']}%"))
        
        if 'email' in args:
            query = query.filter(User.email.ilike(f"%{args['email']}%"))
        
        users = query.order_by(User.created_at.desc()).all()
        return users

@user_bp.route('/<user_id>')
class UserById(MethodView):
    @jwt_required()
    @user_bp.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID."""
        current_user_id = get_jwt_identity()
        
        # Users can only view their own profile
        if user_id != current_user_id:
            abort(403, message="You can only view your own profile")
        
        user = User.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    @user_bp.arguments(UserSchema(partial=True))
    @user_bp.response(200, UserSchema)
    def put(self, user_data, user_id):
        """Update user by ID."""
        current_user_id = get_jwt_identity()
        
        # Users can only update their own profile
        if user_id != current_user_id:
            abort(403, message="You can only update your own profile")
        
        try:
            user = User.query.get_or_404(user_id)
            
            # Check if email is being changed and if it conflicts
            if 'email' in user_data and user_data['email'] != user.email:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user and existing_user.id != user_id:
                    abort(400, message="User with this email already exists")
            
            # Check if name is being changed and if it conflicts
            if 'name' in user_data and user_data['name'] != user.name:
                existing_user = User.query.filter_by(name=user_data['name']).first()
                if existing_user and existing_user.id != user_id:
                    abort(400, message="User with this name already exists")
            
            # Update user fields
            for key, value in user_data.items():
                if key != 'password' and hasattr(user, key):
                    setattr(user, key, value)
            
            # Update password if provided
            if 'password' in user_data and user_data['password']:
                user.set_password(user_data['password'])
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Failed to update user: {str(e)}")
    
    @jwt_required()
    @user_bp.response(204)
    def delete(self, user_id):
        """Delete user by ID."""
        current_user_id = get_jwt_identity()
        
        # Users can only delete their own account
        if user_id != current_user_id:
            abort(403, message="You can only delete your own account")
        
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Failed to delete user: {str(e)}")

@user_bp.route('/<user_id>/stats')
class UserStats(MethodView):
    @jwt_required()
    @user_bp.response(200)
    def get(self, user_id):
        """Get user statistics."""
        current_user_id = get_jwt_identity()
        
        # Users can only view their own stats
        if user_id != current_user_id:
            abort(403, message="You can only view your own statistics")
        
        user = User.query.get_or_404(user_id)
        
        # Calculate total expenses
        total_expenses = 0
        for expense in user.expenses:
            total_expenses += expense.amount
        
        # Calculate account balance
        account_balance = 0
        if user.accounts:
            account_balance = user.accounts[0].balance
        
        # Count categories
        user_categories_count = Category.query.filter_by(user_id=user_id).count()
        
        return {
            "user_id": user_id,
            "total_expenses": total_expenses,
            "account_balance": account_balance,
            "user_categories_count": user_categories_count,
            "total_expenses_count": len(user.expenses)
        }