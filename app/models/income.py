from app import db
from datetime import datetime
import uuid

class Income(db.Model):
    """Income model for tracking money additions to account."""
    __tablename__ = 'incomes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Income {self.id} - {self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'amount': self.amount,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }