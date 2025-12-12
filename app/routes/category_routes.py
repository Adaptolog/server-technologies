from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.category import Category
from app.models.user import User
from app.schemas.category_schema import CategorySchema, CategoryQuerySchema

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories', description='Operations on categories')

@category_bp.route('/')
class Categories(MethodView):
    @jwt_required()
    @category_bp.arguments(CategoryQuerySchema, location='query')
    @category_bp.response(200, CategorySchema(many=True))
    def get(self, args):
        """Get all categories with optional filters."""
        current_user_id = get_jwt_identity()
        
        query = Category.query
        
        if 'name' in args:
            query = query.filter(Category.name.ilike(f"%{args['name']}%"))
        
        if 'is_global' in args:
            query = query.filter_by(is_global=args['is_global'])
        
        # Always filter categories accessible to the user
        query = query.filter(
            (Category.user_id == current_user_id) | 
            (Category.is_global == True) |
            (Category.user_id.is_(None) & Category.is_global == True)
        )
        
        return query.order_by(Category.created_at.desc()).all()
    
    @jwt_required()
    @category_bp.arguments(CategorySchema)
    @category_bp.response(201, CategorySchema)
    def post(self, category_data):
        """Create a new category."""
        current_user_id = get_jwt_identity()
        
        # Users can only create categories for themselves
        if category_data.get('user_id'):
            if category_data['user_id'] != current_user_id:
                abort(403, message="You can only create categories for yourself")
            # User-specific categories are not global
            category_data['is_global'] = False
        else:
            # If no user_id provided, set to current user (personal category)
            category_data['user_id'] = current_user_id
            category_data['is_global'] = False
        
        # Only admins should be able to create global categories
        if category_data.get('is_global', False):
            # Check if user is admin (you might want to implement admin check)
            # For now, disallow creating global categories via this endpoint
            abort(403, message="Only administrators can create global categories")
        
        # Check if category with same name exists for this user
        existing_category = Category.query.filter_by(
            name=category_data['name'],
            user_id=category_data['user_id']
        ).first()
        
        if existing_category:
            abort(400, message="You already have a category with this name")
        
        category = Category(**category_data)
        db.session.add(category)
        db.session.commit()
        return category

@category_bp.route('/<category_id>')
class CategoryById(MethodView):
    @jwt_required()
    @category_bp.response(200, CategorySchema)
    def get(self, category_id):
        """Get category by ID."""
        current_user_id = get_jwt_identity()
        
        category = Category.query.get_or_404(category_id)
        
        # Check if user has access to this category
        if not category.is_global and category.user_id != current_user_id:
            abort(403, message="You don't have access to this category")
        
        return category
    
    @jwt_required()
    @category_bp.arguments(CategorySchema(partial=True))
    @category_bp.response(200, CategorySchema)
    def put(self, category_data, category_id):
        """Update category by ID."""
        current_user_id = get_jwt_identity()
        
        category = Category.query.get_or_404(category_id)
        
        # Users can only update their own categories
        if category.user_id and category.user_id != current_user_id:
            abort(403, message="You can only update your own categories")
        
        # Don't allow changing global categories (only admins should do this)
        if category.is_global:
            abort(403, message="Cannot modify global categories")
        
        # Check if name is being changed and if it conflicts
        if 'name' in category_data and category_data['name'] != category.name:
            existing_category = Category.query.filter_by(
                name=category_data['name'],
                user_id=current_user_id
            ).first()
            
            if existing_category and existing_category.id != category_id:
                abort(400, message="You already have a category with this name")
        
        # Update category fields
        for key, value in category_data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        db.session.commit()
        return category
    
    @jwt_required()
    @category_bp.response(204)
    def delete(self, category_id):
        """Delete category by ID."""
        current_user_id = get_jwt_identity()
        
        category = Category.query.get_or_404(category_id)
        
        # Users can only delete their own categories
        if category.user_id and category.user_id != current_user_id:
            abort(403, message="You can only delete your own categories")
        
        # Don't allow deletion of global categories
        if category.is_global:
            abort(403, message="Cannot delete global categories")
        
        # Check if category has associated expenses
        if category.expenses:
            abort(400, message="Cannot delete category with associated expenses")
        
        db.session.delete(category)
        db.session.commit()
        return '', 204

@category_bp.route('/global')
class GlobalCategories(MethodView):
    @jwt_required()
    @category_bp.response(200, CategorySchema(many=True))
    def get(self):
        """Get all global categories."""
        categories = Category.query.filter_by(is_global=True).order_by(Category.name).all()
        return categories