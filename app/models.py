"""Data models for the expense tracking application"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4


@dataclass
class User:
    """User model"""
    id: str
    name: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Category:
    """Expense category model"""
    id: str
    name: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ExpenseRecord:
    """Expense record model"""
    id: str
    user_id: str
    category_id: str
    created_at: str
    amount: float
    
    def to_dict(self):
        return asdict(self)


class DataStore:
    """In-memory data storage for the application"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.categories: Dict[str, Category] = {}
        self.records: Dict[str, ExpenseRecord] = {}
    
    def add_user(self, name: str) -> User:
        """Add a new user"""
        user_id = str(uuid4())
        user = User(id=user_id, name=name)
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        if user_id in self.users:
            del self.users[user_id]
            # Also delete all user's records
            user_records = [r_id for r_id, record in self.records.items() 
                          if record.user_id == user_id]
            for record_id in user_records:
                del self.records[record_id]
            return True
        return False
    
    def add_category(self, name: str) -> Category:
        """Add a new category"""
        category_id = str(uuid4())
        category = Category(id=category_id, name=name)
        self.categories[category_id] = category
        return category
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get category by ID"""
        return self.categories.get(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return list(self.categories.values())
    
    def delete_category(self, category_id: str) -> bool:
        """Delete category by ID"""
        if category_id in self.categories:
            del self.categories[category_id]
            # Also delete all records in this category
            category_records = [r_id for r_id, record in self.records.items() 
                              if record.category_id == category_id]
            for record_id in category_records:
                del self.records[record_id]
            return True
        return False
    
    def add_record(self, user_id: str, category_id: str, amount: float) -> Optional[ExpenseRecord]:
        """Add a new expense record"""
        # Check if user and category exist
        if user_id not in self.users or category_id not in self.categories:
            return None
        
        record_id = str(uuid4())
        record = ExpenseRecord(
            id=record_id,
            user_id=user_id,
            category_id=category_id,
            created_at=datetime.utcnow().isoformat() + "Z",
            amount=amount
        )
        self.records[record_id] = record
        return record
    
    def get_record(self, record_id: str) -> Optional[ExpenseRecord]:
        """Get record by ID"""
        return self.records.get(record_id)
    
    def get_all_records(self, user_id: Optional[str] = None, 
                       category_id: Optional[str] = None) -> List[ExpenseRecord]:
        """Get records with optional filters"""
        records = list(self.records.values())
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if category_id is not None:
            records = [r for r in records if r.category_id == category_id]
        
        return records
    
    def delete_record(self, record_id: str) -> bool:
        """Delete record by ID"""
        if record_id in self.records:
            del self.records[record_id]
            return True
        return False


# Global data store instance
data_store = DataStore()