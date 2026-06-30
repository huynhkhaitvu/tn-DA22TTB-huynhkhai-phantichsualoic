#!/usr/bin/env python
"""
System Health Check - Backend, GCC, API
"""
import requests
import json
import subprocess

print("=" * 60)
print("🔍 SYSTEM HEALTH CHECK")
print("=" * 60)

API_BASE = 'http://127.0.0.1:5000/api'

# 1. Check Backend Health
print("\n1️⃣  BACKEND STATUS")
print("-" * 60)
try:
    response = requests.get(f'{API_BASE}/health', timeout=2)
    if response.status_code == 200:
        print("✅ Backend: RUNNING")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Backend: Error {response.status_code}")
except Exception as e:
    print(f"❌ Backend: {e}")

# 2. Check GCC
print("\n2️⃣  GCC COMPILER")
print("-" * 60)
try:
    response = requests.get(f'{API_BASE}/check-gcc', timeout=2)
    data = response.json()
    if data['gcc_available']:
        print("✅ GCC: AVAILABLE")
        print(f"   Version: {data['gcc_version']}")
    else:
        print(f"❌ GCC: NOT AVAILABLE")
        print(f"   Error: {data['gcc_version']}")
except Exception as e:
    print(f"❌ GCC Check: {e}")

# 3. Check Gemini API
print("\n3️⃣  GEMINI API")
print("-" * 60)
try:
    response = requests.get(f'{API_BASE}/check-api', timeout=2)
    data = response.json()
    if data['api_available']:
        print("✅ Gemini API: READY")
        print(f"   Message: {data['api_message']}")
    else:
        print(f"⚠️  Gemini API: NOT READY")
        print(f"   Message: {data['api_message']}")
except Exception as e:
    print(f"❌ API Check: {e}")

# 4. Test Authentication
print("\n4️⃣  AUTHENTICATION API")
print("-" * 60)

session = requests.Session()

# Test Register
print("a) Register Test:")
try:
    reg_data = {
        'username': f'testuser_{json.dumps({})}',  # Unique user
        'email': f'test_{hash("test") % 10000}@example.com',
        'password': 'Test@123456',
        'password_confirm': 'Test@123456'
    }
    response = session.post(f'{API_BASE}/auth/register', json=reg_data)
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Register SUCCESS: {result['message']}")
            user_id = result.get('user_id')
        else:
            print(f"   ⚠️  Register: {result.get('error', 'Unknown error')}")
    else:
        print(f"   ❌ Register: HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Register Error: {e}")

# Test Login
print("b) Login Test:")
try:
    login_data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = session.post(f'{API_BASE}/auth/login', json=login_data)
    data = response.json()
    if data.get('success'):
        print(f"   ✅ Login SUCCESS")
        print(f"      Username: {data['username']}")
        print(f"      Email: {data['email']}")
    else:
        print(f"   ⚠️  Login: {data.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   ❌ Login Error: {e}")

# Test Profile
print("c) Profile Test:")
try:
    response = session.get(f'{API_BASE}/auth/profile')
    data = response.json()
    if data.get('success'):
        print(f"   ✅ Profile Retrieved")
        user = data['user']
        print(f"      ID: {user['id']}")
        print(f"      Username: {user['username']}")
        print(f"      Email: {user['email']}")
    else:
        print(f"   ⚠️  Profile: {data.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   ❌ Profile Error: {e}")

# Test Check Auth
print("d) Check Auth Test:")
try:
    response = session.get(f'{API_BASE}/auth/check')
    data = response.json()
    if data.get('authenticated'):
        print(f"   ✅ Authenticated")
        print(f"      User ID: {data['user_id']}")
        print(f"      Username: {data['username']}")
    else:
        print(f"   ⚠️  Not Authenticated")
except Exception as e:
    print(f"   ❌ Check Auth Error: {e}")

# Test Logout
print("e) Logout Test:")
try:
    response = session.post(f'{API_BASE}/auth/logout')
    data = response.json()
    if data.get('success'):
        print(f"   ✅ Logout SUCCESS: {data['message']}")
    else:
        print(f"   ❌ Logout: {data.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   ❌ Logout Error: {e}")

# Check Auth after Logout
print("f) Check Auth After Logout:")
try:
    response = session.get(f'{API_BASE}/auth/check')
    data = response.json()
    if data.get('authenticated'):
        print(f"   ❌ Still Authenticated (logout failed)")
    else:
        print(f"   ✅ Logged out successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ HEALTH CHECK COMPLETE")
print("=" * 60)
