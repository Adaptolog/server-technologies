from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.expense import Expense
from app.models.user import User
from app.models.category import Category
from app.models.account import Account
from app.schemas.expense_schema import ExpenseSchema, ExpenseQuerySchema

expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses', description='Operations on expenses')

@expense_bp.route('/')
class Expenses(MethodView):
    @jwt_required()
    @expense_bp.arguments(ExpenseQuerySchema, location='query')
    @expense_bp.response(200, ExpenseSchema(many=True))
    def get(self, args):
        """Get all expenses with optional filters."""
        current_user_id = get_jwt_identity()
        
        query = Expense.query
        
        # Always filter by current user's expenses
        query = query.filter_by(user_id=current_user_id)
        
        if 'category_id' in args:
            category = Category.query.get(args['category_id'])
            if not category:
                abort(404, message="Category not found")
            
            # Check if user has access to this category
            if not category.is_global and category.user_id != current_user_id:
                abort(403, message="You don't have access to this category")
            
            query = query.filter_by(category_id=args['category_id'])
        
        if 'account_id' in args:
            account = Account.query.get(args['account_id'])
            if not account:
                abort(404, message="Account not found")
            
            # Check if account belongs to user
            if account.user_id != current_user_id:
                abort(403, message="This account doesn't belong to you")
            
            query = query.filter_by(account_id=args['account_id'])
        
        if 'start_date' in args:
            query = query.filter(Expense.created_at >= args['start_date'])
        
        if 'end_date' in args:
            query = query.filter(Expense.created_at <= args['end_date'])
        
        # Add amount filters if needed
        if 'min_amount' in args:
            query = query.filter(Expense.amount >= args['min_amount'])
        
        if 'max_amount' in args:
            query = query.filter(Expense.amount <= args['max_amount'])
        
        return query.order_by(Expense.created_at.desc()).all()
    
    @jwt_required()
    @expense_bp.arguments(ExpenseSchema)
    @expense_bp.response(201, ExpenseSchema)
    def post(self, expense_data):
        """Create a new expense."""
        current_user_id = get_jwt_identity()
        
        # Users can only create expenses for themselves
        if expense_data['user_id'] != current_user_id:
            abort(403, message="You can only create expenses for yourself")
        
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
            abort(403, message="You don't have access to this category")
        
        # Check if account belongs to user
        if account.user_id != user.id:
            abort(403, message="This account doesn't belong to you")
        
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
    @jwt_required()
    @expense_bp.response(200, ExpenseSchema)
    def get(self, expense_id):
        """Get expense by ID."""
        current_user_id = get_jwt_identity()
        
        expense = Expense.query.get_or_404(expense_id)
        
        # Users can only view their own expenses
        if expense.user_id != current_user_id:
            abort(403, message="You can only view your own expenses")
        
        return expense
    
    @jwt_required()
    @expense_bp.response(204)
    def delete(self, expense_id):
        """Delete expense by ID."""
        current_user_id = get_jwt_identity()
        
        expense = Expense.query.get_or_404(expense_id)
        
        # Users can only delete their own expenses
        if expense.user_id != current_user_id:
            abort(403, message="You can only delete your own expenses")
        
        # Return money to account when deleting expense
        account = expense.account
        account.balance += expense.amount
        
        db.session.delete(expense)
        db.session.commit()
        return '', 204
    
    @jwt_required()
    @expense_bp.arguments(ExpenseSchema(partial=True))
    @expense_bp.response(200, ExpenseSchema)
    def put(self, expense_data, expense_id):
        """Update expense by ID."""
        current_user_id = get_jwt_identity()
        
        expense = Expense.query.get_or_404(expense_id)
        
        # Users can only update their own expenses
        if expense.user_id != current_user_id:
            abort(403, message="You can only update your own expenses")
        
        # Store old amount for balance adjustment
        old_amount = expense.amount
        
        # If amount is being updated, adjust account balance
        if 'amount' in expense_data and expense_data['amount'] != old_amount:
            account = expense.account
            
            # First, return old amount to account
            account.balance += old_amount
            
            # Then, check if new amount can be withdrawn
            try:
                account.withdraw(expense_data['amount'])
            except ValueError as e:
                # If withdrawal fails, restore original balance
                account.balance -= old_amount
                db.session.rollback()
                abort(400, message=str(e))
        
        # If category is being updated, validate new category
        if 'category_id' in expense_data and expense_data['category_id'] != expense.category_id:
            category = Category.query.get(expense_data['category_id'])
            if not category:
                abort(404, message="Category not found")
            
            # Check if user has access to this category
            if not category.is_global and category.user_id != current_user_id:
                abort(403, message="You don't have access to this category")
        
        # If account is being updated, validate new account
        if 'account_id' in expense_data and expense_data['account_id'] != expense.account_id:
            account = Account.query.get(expense_data['account_id'])
            if not account:
                abort(404, message="Account not found")
            
            # Check if account belongs to user
            if account.user_id != current_user_id:
                abort(403, message="This account doesn't belong to you")
        
        # Update expense fields
        for key, value in expense_data.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        
        db.session.commit()
        return expense

@expense_bp.route('/summary')
class ExpenseSummary(MethodView):
    @jwt_required()
    @expense_bp.response(200)
    def get(self):
        """Get expense summary for current user."""
        current_user_id = get_jwt_identity()
        
        # Get all expenses for the user
        expenses = Expense.query.filter_by(user_id=current_user_id).all()
        
        if not expenses:
            return {
                "total_expenses": 0,
                "expense_count": 0,
                "average_expense": 0,
                "by_category": {},
                "by_month": {}
            }
        
        # Calculate totals
        total_expenses = sum(expense.amount for expense in expenses)
        expense_count = len(expenses)
        average_expense = total_expenses / expense_count
        
        # Group by category
        by_category = {}
        for expense in expenses:
            category = Category.query.get(expense.category_id)
            category_name = category.name if category else "Unknown"
            
            if category_name not in by_category:
                by_category[category_name] = {
                    "total": 0,
                    "count": 0
                }
            
            by_category[category_name]["total"] += expense.amount
            by_category[category_name]["count"] += 1
        
        # Group by month
        by_month = {}
        for expense in expenses:
            month_key = expense.created_at.strftime("%Y-%m") if expense.created_at else "Unknown"
            
            if month_key not in by_month:
                by_month[month_key] = {
                    "total": 0,
                    "count": 0
                }
            
            by_month[month_key]["total"] += expense.amount
            by_month[month_key]["count"] += 1
        
        return {
            "total_expenses": total_expenses,
            "expense_count": expense_count,
            "average_expense": average_expense,
            "by_category": by_category,
            "by_month": by_month
        }