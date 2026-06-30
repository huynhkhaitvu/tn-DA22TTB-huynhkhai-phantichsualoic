import sqlite3

conn = sqlite3.connect('backend/analyzer.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== SQLite Database Status ===")
print(f"Tables: {[t[0] for t in tables]}\n")

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f"  {table[0]}: {count} records")
    
    # Show table structure
    cursor.execute(f'PRAGMA table_info({table[0]})')
    columns = cursor.fetchall()
    print(f"    Columns: {[col[1] for col in columns]}\n")

conn.close()
