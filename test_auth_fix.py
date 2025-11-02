#!/usr/bin/env python3
"""
Test authentication after fixing JWT configuration
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_auth_fix():
    print("🔧 TESTING AUTH AFTER JWT FIX")
    print("=" * 50)
    
    test_users = [
        {"email": "admin@reelbrief.com", "password": "admin123", "role": "admin"},
        {"email": "sarah@techstartup.com", "password": "client123", "role": "client"},
        {"email": "alex@designer.com", "password": "freelancer123", "role": "freelancer"}
    ]
    
    for user_data in test_users:
        print(f"\n🔐 Testing {user_data['role']} login...")
        print(f"Email: {user_data['email']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": user_data["email"], "password": user_data["password"]},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ LOGIN SUCCESSFUL!")
                print(f"   User: {data.get('user', {}).get('email')}")
                print(f"   Role: {data.get('user', {}).get('role')}")
                print(f"   Token received: {'Yes' if data.get('access_token') else 'No'}")
                
                # Test the token by accessing a protected endpoint
                token = data.get('access_token')
                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                    print(f"   Token validation: {me_response.status_code}")
                    
            elif response.status_code == 401:
                print("❌ Invalid credentials")
                print(f"   Response: {response.json()}")
            elif response.status_code == 500:
                print("❌ Server error - JWT configuration still broken")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text[:200]}...")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    print("\n" + "="*50)
    print("🧪 Testing server health...")
    
    try:
        home_response = requests.get(f"{BASE_URL}/")
        print(f"API Health: {home_response.status_code}")
        if home_response.status_code == 200:
            print("✅ API is running!")
    except Exception as e:
        print(f"❌ Server connectivity issue: {e}")

if __name__ == "__main__":
    test_auth_fix()