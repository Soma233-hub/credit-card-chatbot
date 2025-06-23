"""
Demo data generation script for credit card user database.
This script generates approximately 10,000 users with 1 year of transaction history.
"""

import sqlite3
import random
import datetime
import os
import time

# Ensure the database exists
if not os.path.exists('db/data/credit_card_users.db'):
    print("Database does not exist. Please run create_schema.py first.")
    exit(1)

# Connect to SQLite database
conn = sqlite3.connect('db/data/credit_card_users.db')
cursor = conn.cursor()

# Configuration
NUM_USERS = 10000
START_DATE = datetime.datetime.now() - datetime.timedelta(days=365)
END_DATE = datetime.datetime.now()

# Japanese name components for generating random names
first_names = ["太郎", "次郎", "花子", "裕子", "健太", "直樹", "美咲", "真理", "和也", "拓也", 
               "恵子", "幸子", "大輔", "翔太", "愛", "優子", "健", "陽子", "誠", "裕美"]
last_names = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
              "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水"]

# Email domains
email_domains = ["gmail.com", "yahoo.co.jp", "outlook.jp", "docomo.ne.jp", "ezweb.ne.jp",
                 "softbank.ne.jp", "icloud.com", "hotmail.com", "example.com", "mail.com"]

# Function to generate a random date between start_date and end_date
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    # Handle case where start_date is equal to or later than end_date
    if days_between_dates <= 0:
        return start_date
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

# Function to generate a random amount for purchases
def random_amount():
    # Generate amounts between 100 and 50000 yen
    base = random.randint(1, 500)
    # Make some purchases larger
    if random.random() < 0.1:  # 10% chance for a larger purchase
        base *= random.randint(5, 10)
    return base * 100  # Convert to yen (100, 200, ..., 50000)

# Clear existing data
print("Clearing existing data...")
cursor.execute("DELETE FROM purchases")
cursor.execute("DELETE FROM users")
conn.commit()

# Generate users
print(f"Generating {NUM_USERS} users...")
users = []
for i in range(1, NUM_USERS + 1):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{last_name} {first_name}"

    # Include user_id in email to ensure uniqueness
    email = f"{last_name.lower()}.{first_name.lower()}{i}@{random.choice(email_domains)}"

    # Registration date within the past 3 years
    reg_date = random_date(START_DATE - datetime.timedelta(days=730), END_DATE)

    # Determine user status
    is_active = 1
    is_dormant = 0
    is_cancelled = 0

    # 5% chance user is cancelled
    if random.random() < 0.05:
        is_active = 0
        is_cancelled = 1
        last_activity = random_date(reg_date, END_DATE)
    # 15% chance user is dormant (inactive but not cancelled)
    elif random.random() < 0.15:
        is_dormant = 1
        last_activity = random_date(reg_date, END_DATE - datetime.timedelta(days=90))
    else:
        last_activity = random_date(max(reg_date, END_DATE - datetime.timedelta(days=30)), END_DATE)

    users.append((
        i,  # user_id
        name,
        email,
        reg_date.strftime('%Y-%m-%d'),
        is_active,
        is_dormant,
        is_cancelled,
        last_activity.strftime('%Y-%m-%d')
    ))

    if i % 1000 == 0:
        print(f"Generated {i} users")

# Insert users in batches
batch_size = 1000
for i in range(0, len(users), batch_size):
    batch = users[i:i+batch_size]
    cursor.executemany('''
    INSERT INTO users (user_id, name, email, registration_date, is_active, is_dormant, is_cancelled, last_activity_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', batch)
    conn.commit()
    print(f"Inserted users {i+1} to {min(i+batch_size, len(users))}")

# Get category IDs
cursor.execute("SELECT category_id FROM categories")
category_ids = [row[0] for row in cursor.fetchall()]

# Generate purchases
print("Generating purchases...")
purchases = []
purchase_id = 1

# Different purchase patterns based on user activity
for user_id, _, _, reg_date_str, is_active, is_dormant, is_cancelled, last_activity_str in users:
    reg_date = datetime.datetime.strptime(reg_date_str, '%Y-%m-%d')
    last_activity = datetime.datetime.strptime(last_activity_str, '%Y-%m-%d')

    # Skip generating purchases for cancelled users
    if is_cancelled == 1:
        continue

    # Determine number of purchases based on user status
    if is_dormant == 1:
        # Dormant users have fewer purchases and none recent
        num_purchases = random.randint(1, 20)
        purchase_end_date = last_activity
    else:
        # Active users have more purchases
        num_purchases = random.randint(20, 100)
        purchase_end_date = END_DATE

    # Generate purchases for this user
    for _ in range(num_purchases):
        purchase_date = random_date(max(reg_date, START_DATE), purchase_end_date)

        # Determine category preferences (some users prefer certain categories)
        if random.random() < 0.7:  # 70% of purchases follow user preferences
            # Create weighted preferences for this user
            preferences = {cat_id: random.random() for cat_id in category_ids}
            # Sort by preference value and take top 3
            preferred_cats = sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:3]
            category_id = preferred_cats[0][0]
        else:
            category_id = random.choice(category_ids)

        amount = random_amount()

        purchases.append((
            purchase_id,
            user_id,
            amount,
            purchase_date.strftime('%Y-%m-%d'),
            category_id
        ))

        purchase_id += 1

        if purchase_id % 10000 == 0:
            print(f"Generated {purchase_id} purchases")

# Insert purchases in batches
for i in range(0, len(purchases), batch_size):
    batch = purchases[i:i+batch_size]
    cursor.executemany('''
    INSERT INTO purchases (purchase_id, user_id, amount, purchase_date, category_id)
    VALUES (?, ?, ?, ?, ?)
    ''', batch)
    conn.commit()
    print(f"Inserted purchases {i+1} to {min(i+batch_size, len(purchases))}")

# Print statistics
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM purchases")
purchase_count = cursor.fetchone()[0]

print(f"\nDemo data generation complete!")
print(f"Generated {user_count} users and {purchase_count} purchases.")

# Close connection
conn.close()
