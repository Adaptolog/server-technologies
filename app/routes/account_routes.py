from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.account import Account
from app.models.income import Income
from app.models.user import User
from app.schemas.account_schema import (
    AccountSchema, 
    AccountQuerySchema, 
    IncomeSchema,
    IncomeQuerySchema
)

account_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts', description='Operations on accounts')

@account_bp.route('/')
class Accounts(MethodView):
    @jwt_required()
    @account_bp.arguments(AccountQuerySchema, location='query')
    @account_bp.response(200, AccountSchema(many=True))
    def get(self, args):
        """Get all accounts with optional filters."""
        current_user_id = get_jwt_identity()
        
        query = Account.query
        
        if 'user_id' in args:
            # Users can only see their own accounts
            if args['user_id'] != current_user_id:
                abort(403, message="You can only view your own accounts")
            
            user = User.query.get(args['user_id'])
            if not user:
                abort(404, message="User not found")
            query = query.filter_by(user_id=args['user_id'])
        else:
            # If no user_id provided, show only current user's accounts
            query = query.filter_by(user_id=current_user_id)
        
        return query.order_by(Account.created_at.desc()).all()
    
    @jwt_required()
    @account_bp.arguments(AccountSchema)
    @account_bp.response(201, AccountSchema)
    def post(self, account_data):
        """Create a new account."""
        current_user_id = get_jwt_identity()
        
        # Users can only create accounts for themselves
        if account_data['user_id'] != current_user_id:
            abort(403, message="You can only create accounts for yourself")
        
        # Check if user exists
        user = User.query.get(account_data['user_id'])
        if not user:
            abort(404, message="User not found")
        
        # Check if user already has an account
        existing_account = Account.query.filter_by(user_id=account_data['user_id']).first()
        if existing_account:
            abort(400, message="User already has an account")
        
        account = Account(**account_data)
        db.session.add(account)
        db.session.commit()
        
        return account

@account_bp.route('/<account_id>')
class AccountById(MethodView):
    @jwt_required()
    @account_bp.response(200, AccountSchema)
    def get(self, account_id):
        """Get account by ID."""
        current_user_id = get_jwt_identity()
        
        account = Account.query.get_or_404(account_id)
        
        # Users can only view their own accounts
        if account.user_id != current_user_id:
            abort(403, message="You can only view your own accounts")
        
        return account
    
    @jwt_required()
    @account_bp.response(204)
    def delete(self, account_id):
        """Delete account by ID."""
        current_user_id = get_jwt_identity()
        
        account = Account.query.get_or_404(account_id)
        
        # Users can only delete their own accounts
        if account.user_id != current_user_id:
            abort(403, message="You can only delete your own accounts")
        
        # Check if account has transactions
        if account.incomes or account.expenses:
            abort(400, message="Cannot delete account with transactions")
        
        db.session.delete(account)
        db.session.commit()
        return '', 204

@account_bp.route('/<account_id>/income')
class AccountIncome(MethodView):
    @jwt_required()
    @account_bp.arguments(IncomeSchema)
    @account_bp.response(201, IncomeSchema)
    def post(self, income_data, account_id):
        """Add income to account."""
        current_user_id = get_jwt_identity()
        
        account = Account.query.get_or_404(account_id)
        
        # Users can only add income to their own accounts
        if account.user_id != current_user_id:
            abort(403, message="You can only add income to your own accounts")
        
        try:
            # Add income and update balance
            income = account.add_income(
                amount=income_data['amount'],
                description=income_data.get('description', '')
            )
        except ValueError as e:
            abort(400, message=str(e))
        
        db.session.add(income)
        db.session.commit()
        
        return income
    
    @jwt_required()
    @account_bp.arguments(IncomeQuerySchema, location='query')
    @account_bp.response(200, IncomeSchema(many=True))
    def get(self, args, account_id):
        """Get income history for account."""
        current_user_id = get_jwt_identity()
        
        account = Account.query.get_or_404(account_id)
        
        # Users can only view income for their own accounts
        if account.user_id != current_user_id:
            abort(403, message="You can only view income for your own accounts")
        
        query = Income.query.filter_by(account_id=account_id)
        
        if 'start_date' in args:
            query = query.filter(Income.created_at >= args['start_date'])
        
        if 'end_date' in args:
            query = query.filter(Income.created_at <= args['end_date'])
        
        return query.order_by(Income.created_at.desc()).all()

@account_bp.route('/<account_id>/balance')
class AccountBalance(MethodView):
    @jwt_required()
    @account_bp.response(200)
    def get(self, account_id):
        """Get account balance."""
        current_user_id = get_jwt_identity()
        
        account = Account.query.get_or_404(account_id)
        
        # Users can only view balance of their own accounts
        if account.user_id != current_user_id:
            abort(403, message="You can only view balance of your own accounts")
        
        return {
            "account_id": account_id,
            "balance": account.balance,
            "user_id": account.user_id
        }

@account_bp.route('/user/<user_id>')
class UserAccount(MethodView):
    @jwt_required()
    @account_bp.response(200, AccountSchema)
    def get(self, user_id):
        """Get account for a specific user."""
        current_user_id = get_jwt_identity()
        
        # Users can only view their own account
        if user_id != current_user_id:
            abort(403, message="You can only view your own account")
        
        account = Account.query.filter_by(user_id=user_id).first()
        if not account:
            abort(404, message="Account not found for this user")
        
        return account