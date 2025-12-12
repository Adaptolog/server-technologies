from app import db
from datetime import datetime
import uuid

class Account(db.Model):
    """Account model for tracking income and expenses."""
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incomes = db.relationship('Income', backref='account', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': self.balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def add_income(self, amount, description=""):
        """Add income to account."""
        from app.models.income import Income
        if amount <= 0:
            raise ValueError("Income amount must be positive")
        
        income = Income(
            account_id=self.id,
            amount=amount,
            description=description
        )
        self.balance += amount
        return income
    
    def can_withdraw(self, amount):
        """Check if account has sufficient funds."""
        return self.balance >= amount
    
    def withdraw(self, amount):
        """Withdraw amount from account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.can_withdraw(amount):
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        return True