"""
Database schema creation script for credit card user database.
This script creates the necessary tables for storing credit card user data.
"""

import sqlite3
import os

# Create db directory if it doesn't exist
os.makedirs('db/data', exist_ok=True)

# Connect to SQLite database (will be created if it doesn't exist)
conn = sqlite3.connect('db/data/credit_card_users.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    registration_date TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,  -- 1 for active, 0 for inactive
    is_dormant INTEGER NOT NULL DEFAULT 0,  -- 1 for dormant, 0 for not dormant
    is_cancelled INTEGER NOT NULL DEFAULT 0,  -- 1 for cancelled, 0 for not cancelled
    last_activity_date TEXT
)
''')

# Create purchase categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
)
''')

# Create purchases table
cursor.execute('''
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    purchase_date TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
)
''')

# Insert default categories
categories = [
    (1, '食品'),
    (2, '衣料品'),
    (3, '美容'),
    (4, '旅行'),
    (5, 'エンターテイメント'),
    (6, '交通'),
    (7, '住居'),
    (8, '医療'),
    (9, '教育'),
    (10, 'ペット'),
    (11, 'その他')
]

cursor.executemany('INSERT OR IGNORE INTO categories (category_id, category_name) VALUES (?, ?)', categories)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database schema created successfully.")