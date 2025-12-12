from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app import db
from app.models.category import Category
from app.models.user import User
from app.schemas.category_schema import CategorySchema, CategoryQuerySchema

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories', description='Operations on categories')

@category_bp.route('/')
class Categories(MethodView):
    @category_bp.arguments(CategoryQuerySchema, location='query')
    @category_bp.response(200, CategorySchema(many=True))
    def get(self, args):
        """Get all categories with optional filters."""
        query = Category.query
        
        if 'name' in args:
            query = query.filter(Category.name.ilike(f"%{args['name']}%"))
        
        if 'is_global' in args:
            query = query.filter_by(is_global=args['is_global'])
        
        if 'user_id' in args:
            if args['user_id']:
                query = query.filter(
                    (Category.user_id == args['user_id']) | (Category.is_global == True)
                )
        
        return query.order_by(Category.created_at.desc()).all()
    
    @category_bp.arguments(CategorySchema)
    @category_bp.response(201, CategorySchema)
    def post(self, category_data):
        """Create a new category."""
        # Validate user exists if user_id is provided
        if category_data.get('user_id'):
            user = User.query.get(category_data['user_id'])
            if not user:
                abort(404, message="User not found")
            # User-specific categories are not global
            category_data['is_global'] = False
        
        # Check if category with same name exists for this user/global
        query = Category.query.filter_by(name=category_data['name'])
        if category_data.get('user_id'):
            query = query.filter(
                (Category.user_id == category_data['user_id']) | 
                (Category.is_global == True)
            )
        else:
            query = query.filter_by(is_global=True)
        
        existing_category = query.first()
        if existing_category:
            abort(400, message="Category with this name already exists")
        
        category = Category(**category_data)
        db.session.add(category)
        db.session.commit()
        return category

@category_bp.route('/<category_id>')
class CategoryById(MethodView):
    @category_bp.response(200, CategorySchema)
    def get(self, category_id):
        """Get category by ID."""
        category = Category.query.get_or_404(category_id)
        return category
    
    @category_bp.arguments(CategorySchema)
    @category_bp.response(200, CategorySchema)
    def put(self, category_data, category_id):
        """Update category by ID."""
        category = Category.query.get_or_404(category_id)
        
        # Check if name is being changed and if it conflicts
        if 'name' in category_data and category_data['name'] != category.name:
            query = Category.query.filter_by(name=category_data['name'])
            if category.user_id:
                query = query.filter(
                    (Category.user_id == category.user_id) | 
                    (Category.is_global == True)
                )
            else:
                query = query.filter_by(is_global=True)
            
            existing_category = query.first()
            if existing_category and existing_category.id != category_id:
                abort(400, message="Category with this name already exists")
        
        for key, value in category_data.items():
            setattr(category, key, value)
        
        db.session.commit()
        return category
    
    @category_bp.response(204)
    def delete(self, category_id):
        """Delete category by ID."""
        category = Category.query.get_or_404(category_id)
        
        # Don't allow deletion of global categories with expenses
        if category.is_global and category.expenses:
            abort(400, message="Cannot delete global category with associated expenses")
        
        db.session.delete(category)
        db.session.commit()
        return '', 204