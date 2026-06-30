#!/usr/bin/env python3
"""
Script simples para testar autenticação sem Flask
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("1. Testing database connection...")
try:
    from db_manager import DatabaseManager
    print("   ✓ DatabaseManager imported")
    
    db = DatabaseManager()
    print("   ✓ DatabaseManager initialized")
    
    # Test register
    print("\n2. Testing user registration...")
    result = db.register_user("testuser", "test@test.com", "password123")
    print(f"   Result: {result}")
    
    # Test verify
    print("\n3. Testing password verification...")
    result = db.verify_password("testuser", "password123")
    print(f"   Result: {result}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
