import requests
url='http://127.0.0.1:5000/api/auth/login'
resp=requests.post(url, json={'username':'testuser','password':'password123'}, timeout=10)
print(resp.status_code)
print(resp.headers.get('Content-Type'))
print(resp.text)
