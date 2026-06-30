import sys
sys.path.insert(0, 'backend')
from db_manager import DatabaseManager
import sqlite3

# Xóa DB cũ và tạo mới
import os
if os.path.exists('backend/analyzer.db'):
    os.remove('backend/analyzer.db')

db = DatabaseManager('backend/analyzer.db')

# Kiểm tra tables
conn = sqlite3.connect('backend/analyzer.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== Database Tables ===")
for table in tables:
    print(f"\n{table[0]}:")
    cursor.execute(f'PRAGMA table_info({table[0]})')
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()

# Test register user
print("\n=== Testing User Registration ===")
result = db.register_user('testuser', 'test@example.com', 'password123')
print(f"Register result: {result}")

# Test login
print("\n=== Testing User Login ===")
login_result = db.verify_password('testuser', 'password123')
print(f"Login result: {login_result}")
