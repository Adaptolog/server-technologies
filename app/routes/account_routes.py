from flask.views import MethodView
from flask_smorest import Blueprint, abort
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
    @account_bp.arguments(AccountQuerySchema, location='query')
    @account_bp.response(200, AccountSchema(many=True))
    def get(self, args):
        """Get all accounts with optional filters."""
        query = Account.query
        
        if 'user_id' in args:
            user = User.query.get(args['user_id'])
            if not user:
                abort(404, message="User not found")
            query = query.filter_by(user_id=args['user_id'])
        
        return query.order_by(Account.created_at.desc()).all()
    
    @account_bp.arguments(AccountSchema)
    @account_bp.response(201, AccountSchema)
    def post(self, account_data):
        """Create a new account."""
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
    @account_bp.response(200, AccountSchema)
    def get(self, account_id):
        """Get account by ID."""
        account = Account.query.get_or_404(account_id)
        return account
    
    @account_bp.response(204)
    def delete(self, account_id):
        """Delete account by ID."""
        account = Account.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        return '', 204

@account_bp.route('/<account_id>/income')
class AccountIncome(MethodView):
    @account_bp.arguments(IncomeSchema)
    @account_bp.response(201, IncomeSchema)
    def post(self, income_data, account_id):
        """Add income to account."""
        account = Account.query.get_or_404(account_id)
        
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
    
    @account_bp.arguments(IncomeQuerySchema, location='query')
    @account_bp.response(200, IncomeSchema(many=True))
    def get(self, args, account_id):
        """Get income history for account."""
        account = Account.query.get_or_404(account_id)
        
        query = Income.query.filter_by(account_id=account_id)
        
        if 'start_date' in args:
            query = query.filter(Income.created_at >= args['start_date'])
        
        if 'end_date' in args:
            query = query.filter(Income.created_at <= args['end_date'])
        
        return query.order_by(Income.created_at.desc()).all()

@account_bp.route('/<account_id>/balance')
class AccountBalance(MethodView):
    @account_bp.response(200, AccountSchema)
    def get(self, account_id):
        """Get account balance."""
        account = Account.query.get_or_404(account_id)
        return account