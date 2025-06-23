"""
Database connection module using SQLAlchemy.
This module provides a flexible way to connect to different databases.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base class for all models
Base = declarative_base()

class DatabaseConnection:
    """
    A class to manage database connections with support for different database types.
    Currently supports SQLite, but can be extended to support other databases.
    """
    
    def __init__(self, db_type="sqlite", db_path=None, db_host=None, db_port=None, 
                 db_name=None, db_user=None, db_password=None):
        """
        Initialize database connection.
        
        Args:
            db_type (str): Type of database ('sqlite', 'mysql', 'postgresql', etc.)
            db_path (str): Path to SQLite database file
            db_host (str): Database host
            db_port (str): Database port
            db_name (str): Database name
            db_user (str): Database user
            db_password (str): Database password
        """
        self.db_type = db_type
        self.db_path = db_path or os.getenv('DB_PATH', 'db/data/credit_card_users.db')
        self.db_host = db_host or os.getenv('DB_HOST')
        self.db_port = db_port or os.getenv('DB_PORT')
        self.db_name = db_name or os.getenv('DB_NAME')
        self.db_user = db_user or os.getenv('DB_USER')
        self.db_password = db_password or os.getenv('DB_PASSWORD')
        
        self.engine = None
        self.Session = None
        
    def connect(self):
        """
        Create database connection based on the database type.
        
        Returns:
            sqlalchemy.engine: SQLAlchemy engine
        """
        if self.db_type.lower() == 'sqlite':
            # SQLite connection
            connection_string = f'sqlite:///{self.db_path}'
            self.engine = create_engine(connection_string)
        elif self.db_type.lower() == 'mysql':
            # MySQL connection
            connection_string = f'mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
            self.engine = create_engine(connection_string)
        elif self.db_type.lower() == 'postgresql':
            # PostgreSQL connection
            connection_string = f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
            self.engine = create_engine(connection_string)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        
        return self.engine
    
    def get_session(self):
        """
        Get a new session.
        
        Returns:
            sqlalchemy.orm.session.Session: SQLAlchemy session
        """
        if not self.Session:
            self.connect()
        
        return self.Session()

# Default database connection
def get_db_connection(db_type=None, db_path=None, db_host=None, db_port=None, 
                      db_name=None, db_user=None, db_password=None):
    """
    Get database connection with the specified parameters or environment variables.
    
    Args:
        db_type (str): Type of database ('sqlite', 'mysql', 'postgresql', etc.)
        db_path (str): Path to SQLite database file
        db_host (str): Database host
        db_port (str): Database port
        db_name (str): Database name
        db_user (str): Database user
        db_password (str): Database password
        
    Returns:
        DatabaseConnection: Database connection object
    """
    db_type = db_type or os.getenv('DB_TYPE', 'sqlite')
    
    return DatabaseConnection(
        db_type=db_type,
        db_path=db_path,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password
    )
