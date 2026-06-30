import sys
import sqlite3
sys.path.insert(0, r'D:\DATN\XAY-DUNG-MA-HE-THONG-PHAN-TICH-GOI-Y-SUA-LOI-MA-NGUON-C\backend')
import app as backend_app

client = backend_app.app.test_client()
login_resp = client.post('/api/auth/login', json={'username': 'admin', 'password': 'j'})
print('login', login_resp.status_code, login_resp.get_json())
resp = client.post('/api/analyze', json={
    'code': '#include <stdio.h>\nint main(){int a=1;printf("%d",a);return 0;}',
    'problem_id': 1,
    'testcases': [{'input': '5', 'expected_output': '15'}],
    'requirements': 'sum 1..n'
})
print('analyze', resp.status_code, resp.get_json())
con = sqlite3.connect(r'D:\DATN\XAY-DUNG-MA-HE-THONG-PHAN-TICH-GOI-Y-SUA-LOI-MA-NGUON-C\backend\data\app.sqlite')
cur = con.cursor()
print('phan_tich_ai_count', cur.execute('SELECT COUNT(*) FROM phan_tich_ai').fetchone()[0])
print('latest_ai', cur.execute('SELECT id, nop_bai_id, phan_loai FROM phan_tich_ai ORDER BY id DESC LIMIT 1').fetchone())
con.close()
