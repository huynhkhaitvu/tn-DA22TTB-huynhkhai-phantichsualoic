#!/usr/bin/env python
"""
Test script để kiểm tra Authentication API
"""
import requests
import json

API_BASE = 'http://127.0.0.1:5000/api'

def test_register():
    print("\n=== TEST REGISTER ===")
    data = {
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }
    response = requests.post(f'{API_BASE}/auth/register', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

def test_login():
    print("\n=== TEST LOGIN ===")
    data = {
        'username': 'testuser2',
        'password': 'password123'
    }
    session = requests.Session()
    response = session.post(f'{API_BASE}/auth/login', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Cookies: {session.cookies}")
    return session

def test_profile(session):
    print("\n=== TEST GET PROFILE ===")
    response = session.get(f'{API_BASE}/auth/profile')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

def test_check_auth(session):
    print("\n=== TEST CHECK AUTH ===")
    response = session.get(f'{API_BASE}/auth/check')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

def test_logout(session):
    print("\n=== TEST LOGOUT ===")
    response = session.post(f'{API_BASE}/auth/logout')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

def test_invalid_login():
    print("\n=== TEST INVALID LOGIN ===")
    data = {
        'username': 'wronguser',
        'password': 'wrongpass'
    }
    response = requests.post(f'{API_BASE}/auth/login', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

if __name__ == '__main__':
    print("Starting Authentication API Tests...")
    print(f"API Base: {API_BASE}")
    
    try:
        # Test register
        test_register()
        
        # Test login
        session = test_login()
        
        # Test get profile
        test_profile(session)
        
        # Test check auth
        test_check_auth(session)
        
        # Test logout
        test_logout(session)
        
        # Test check auth after logout
        test_check_auth(session)
        
        # Test invalid login
        test_invalid_login()
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
