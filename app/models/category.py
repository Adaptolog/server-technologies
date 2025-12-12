from app import db
from datetime import datetime
import uuid

class Category(db.Model):
    """Expense category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    is_global = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_global': self.is_global,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }