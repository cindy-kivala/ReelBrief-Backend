#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_basic_users():
    print("🔍 Testing Basic Users")
    print("=" * 50)
    
    test_users = [
        {"email": "admin@reelbrief.com", "password": "admin123", "role": "admin"},
        {"email": "freelancer@reelbrief.com", "password": "freelancer123", "role": "freelancer"},
        {"email": "client@reelbrief.com", "password": "client123", "role": "client"},
    ]
    
    for user in test_users:
        print(f"\n🔐 Testing: {user['email']} ({user['role']})")
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    print("✅ Login successful!")
                    
                    # Test basic endpoints
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    # Test /api/auth/me
                    me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                    if me_response.status_code == 200:
                        user_info = me_response.json()
                        print(f"   👤 User: {user_info.get('first_name')} {user_info.get('last_name')}")
                        print(f"   🏷️  Role: {user_info.get('role')}")
                    
                    # Test a few endpoints based on role
                    endpoints_to_test = ['/api/users/', '/api/projects/']
                    for endpoint in endpoints_to_test:
                        endpoint_response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                        print(f"   📡 {endpoint}: {endpoint_response.status_code}")
                    
                    break
            else:
                print(f"❌ Login failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Basic user testing completed!")

if __name__ == "__main__":
    test_basic_users()
