from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app import db
from app.models.expense import Expense
from app.models.user import User
from app.models.category import Category
from app.models.account import Account
from app.schemas.expense_schema import ExpenseSchema, ExpenseQuerySchema

expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses', description='Operations on expenses')

@expense_bp.route('/')
class Expenses(MethodView):
    @expense_bp.arguments(ExpenseQuerySchema, location='query')
    @expense_bp.response(200, ExpenseSchema(many=True))
    def get(self, args):
        """Get all expenses with optional filters."""
        query = Expense.query
        
        if 'user_id' in args:
            user = User.query.get(args['user_id'])
            if not user:
                abort(404, message="User not found")
            query = query.filter_by(user_id=args['user_id'])
        
        if 'category_id' in args:
            category = Category.query.get(args['category_id'])
            if not category:
                abort(404, message="Category not found")
            query = query.filter_by(category_id=args['category_id'])
        
        if 'account_id' in args:
            account = Account.query.get(args['account_id'])
            if not account:
                abort(404, message="Account not found")
            query = query.filter_by(account_id=args['account_id'])
        
        if 'start_date' in args:
            query = query.filter(Expense.created_at >= args['start_date'])
        
        if 'end_date' in args:
            query = query.filter(Expense.created_at <= args['end_date'])
        
        return query.order_by(Expense.created_at.desc()).all()
    
    @expense_bp.arguments(ExpenseSchema)
    @expense_bp.response(201, ExpenseSchema)
    def post(self, expense_data):
        """Create a new expense."""
        # Validate user exists
        user = User.query.get(expense_data['user_id'])
        if not user:
            abort(404, message="User not found")
        
        # Validate category exists
        category = Category.query.get(expense_data['category_id'])
        if not category:
            abort(404, message="Category not found")
        
        # Validate account exists
        account = Account.query.get(expense_data['account_id'])
        if not account:
            abort(404, message="Account not found")
        
        # Check if user has access to this category
        if not category.is_global and category.user_id != user.id:
            abort(403, message="User does not have access to this category")
        
        # Check if account belongs to user
        if account.user_id != user.id:
            abort(403, message="Account does not belong to this user")
        
        try:
            # Withdraw amount from account
            account.withdraw(expense_data['amount'])
        except ValueError as e:
            abort(400, message=str(e))
        
        # Create expense
        expense = Expense(**expense_data)
        db.session.add(expense)
        db.session.commit()
        
        return expense

@expense_bp.route('/<expense_id>')
class ExpenseById(MethodView):
    @expense_bp.response(200, ExpenseSchema)
    def get(self, expense_id):
        """Get expense by ID."""
        expense = Expense.query.get_or_404(expense_id)
        return expense
    
    @expense_bp.response(204)
    def delete(self, expense_id):
        """Delete expense by ID."""
        expense = Expense.query.get_or_404(expense_id)
        
        # Return money to account when deleting expense
        account = expense.account
        account.balance += expense.amount
        
        db.session.delete(expense)
        db.session.commit()
        return '', 204