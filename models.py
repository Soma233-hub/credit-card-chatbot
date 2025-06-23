"""
SQLAlchemy models for the credit card user database.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.db_connection import Base

class User(Base):
    """
    User model representing credit card users.
    """
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    registration_date = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    is_dormant = Column(Integer, default=0)
    is_cancelled = Column(Integer, default=0)
    last_activity_date = Column(String)
    
    # Relationship with purchases
    purchases = relationship("Purchase", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.user_id}, name={self.name}, active={self.is_active})>"

class Category(Base):
    """
    Category model representing purchase categories.
    """
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False, unique=True)
    
    # Relationship with purchases
    purchases = relationship("Purchase", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.category_id}, name={self.category_name})>"

class Purchase(Base):
    """
    Purchase model representing credit card purchases.
    """
    __tablename__ = 'purchases'
    
    purchase_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)
    purchase_date = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    category = relationship("Category", back_populates="purchases")
    
    def __repr__(self):
        return f"<Purchase(id={self.purchase_id}, user_id={self.user_id}, amount={self.amount})>"