import os
import sqlite3

path = os.path.join('backend', 'data', 'app.sqlite')
print('DB exists:', os.path.exists(path))
conn = sqlite3.connect(path)
cur = conn.cursor()
print('TABLES:')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print('-', row[0])
print('\nmo_hinh_ai schema:')
for row in cur.execute('PRAGMA table_info(mo_hinh_ai)'):
    print(row)
print('\nmo_hinh_ai rows:')
for row in cur.execute('SELECT id, nop_bai_id, phan_loai, created_at FROM mo_hinh_ai ORDER BY id DESC LIMIT 10'):
    print(row)
conn.close()
