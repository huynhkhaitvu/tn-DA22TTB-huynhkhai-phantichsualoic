#!/usr/bin/env python3
"""
Test script - Kiểm tra setup của hệ thống
"""
import sys
import os
import subprocess
import platform

def test_python():
    """Kiểm tra Python"""
    print("[1/5] Checking Python...")
    version = sys.version
    print(f"✅ Python {version}")
    return True

def test_gcc():
    """Kiểm tra GCC"""
    print("\n[2/5] Checking GCC...")
    try:
        result = subprocess.run(['gcc', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ GCC found:\n{result.stdout.split(chr(10))[0]}")
            return True
        else:
            print("❌ GCC command failed")
            return False
    except FileNotFoundError:
        print("❌ GCC not found in PATH")
        print("   Please install MinGW-w64 and add to PATH")
        print("   See INSTALL_GCC.md for instructions")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_flask_imports():
    """Kiểm tra Flask imports"""
    print("\n[3/5] Checking Flask dependencies...")
    try:
        import flask
        import flask_cors
        import dotenv
        import requests
        print("✅ All Flask dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def test_env_file():
    """Kiểm tra .env file"""
    print("\n[4/5] Checking .env configuration...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content and 'AIzaSy' in content:
                print("✅ .env file found with API key")
                return True
            else:
                print("⚠️  .env file found but API key missing")
                return False
    else:
        print("❌ .env file not found")
        print("   Copy .env.example to .env and add your API key")
        return False

def test_compile_sample():
    """Kiểm tra biên dịch file C mẫu"""
    print("\n[5/5] Testing C compilation...")
    
    test_code = '''
#include <stdio.h>
int main() {
    printf("Test OK");
    return 0;
}
'''
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        c_file = f.name
    
    exe_file = c_file.replace('.c', '.exe')
    
    try:
        result = subprocess.run(['gcc', c_file, '-o', exe_file],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Test chạy
            run_result = subprocess.run([exe_file],
                                      capture_output=True, text=True, timeout=5)
            if 'Test OK' in run_result.stdout:
                print("✅ C compilation and execution works")
                return True
            else:
                print("❌ Program did not produce expected output")
                return False
        else:
            print(f"❌ Compilation failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Cleanup
        for f in [c_file, exe_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def main():
    """Main test runner"""
    print("=" * 50)
    print("C Code Analyzer - System Test")
    print("=" * 50)
    
    tests = [
        test_python,
        test_gcc,
        test_flask_imports,
        test_env_file,
        test_compile_sample
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("\n✅ All systems ready! You can now run:")
        print("   python app.py")
        return 0
    else:
        print("\n❌ Some tests failed. Fix issues above and try again.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
