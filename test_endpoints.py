#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            if response.content:
                try:
                    return response.json()
                except:
                    return response.text
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection refused (is Flask running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("🔍 Testing ReelBrief API Endpoints")
    print("=" * 50)
    
    # Test basic health/root endpoint
    print("\n1. Testing Basic Endpoints:")
    test_endpoint('GET', '/')
    
    # Test user endpoints
    print("\n2. Testing User Endpoints:")
    test_endpoint('GET', '/api/users')
    
    # Test freelancer profile endpoints
    print("\n3. Testing Freelancer Profile Endpoints:")
    test_endpoint('GET', '/api/freelancer-profiles')
    
    # Test skill endpoints
    print("\n4. Testing Skill Endpoints:")
    test_endpoint('GET', '/api/skills')
    
    # Test project endpoints
    print("\n5. Testing Project Endpoints:")
    test_endpoint('GET', '/api/projects')
    
    # Test authentication endpoints (if they exist)
    print("\n6. Testing Auth Endpoints:")
    test_endpoint('POST', '/api/auth/login', {'email': 'test@test.com', 'password': 'test'}, 401)  # Should fail with bad credentials
    
    # Test specific model relationships
    print("\n7. Testing Specific Endpoints:")
    
    # If we have any users, test their profiles
    users = test_endpoint('GET', '/api/users')
    if users and isinstance(users, list) and len(users) > 0:
        user_id = users[0]['id']
        test_endpoint('GET', f'/api/users/{user_id}')
        test_endpoint('GET', f'/api/users/{user_id}/freelancer-profile')
    
    print("\n" + "=" * 50)
    print("🎉 Endpoint testing completed!")

if __name__ == "__main__":
    main()
