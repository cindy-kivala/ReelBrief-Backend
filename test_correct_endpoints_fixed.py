#!/usr/bin/env python3
import requests
import json
import random

BASE_URL = "http://127.0.0.1:5000"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.user_id = None
    
    def register_and_login(self):
        """Register a new user and login with correct field names"""
        test_id = random.randint(1000, 9999)
        user_data = {
            "email": f"test{test_id}@reelbrief.com", 
            "password": "testpassword123",
            "role": "freelancer",
            "first_name": f"Test{test_id}",
            "last_name": f"User{test_id}",
            "username": f"testuser{test_id}"
        }
        
        print(f"�� Registering user: {user_data['email']}")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.token = data.get('token')
            if self.token:
                self.headers = {'Authorization': f'Bearer {self.token}'}
                print("✅ Registration and login successful!")
                return True
            else:
                print("❌ No token received after registration")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
        
        # If registration fails, try to login with existing demo account
        return self.try_demo_login()
    
    def try_demo_login(self):
        """Try to login with demo credentials"""
        print("�� Trying demo credentials...")
        demo_logins = [
            {"email": "demo@reelbrief.com", "password": "demo123"},
            {"email": "test@reelbrief.com", "password": "test123"},
            {"email": "admin@reelbrief.com", "password": "admin123"},
            {"email": "freelancer@reelbrief.com", "password": "freelancer123"},
            {"email": "client@reelbrief.com", "password": "client123"}
        ]
        
        for creds in demo_logins:
            print(f"   Trying: {creds['email']}")
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=creds)
            if login_resp.status_code == 200:
                data = login_resp.json()
                self.token = data.get('token')
                if self.token:
                    self.headers = {'Authorization': f'Bearer {self.token}'}
                    print(f"✅ Logged in as: {creds['email']}")
                    return True
            else:
                print(f"   ❌ Failed: {creds['email']} - {login_resp.status_code}")
        
        print("❌ No valid credentials found")
        return False
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers=self.headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                print(f"❌ Unknown method: {method}")
                return False
            
            if response.status_code == expected_status:
                print(f"✅ {method} {endpoint} - Status: {response.status_code}")
                if response.content:
                    try:
                        result = response.json()
                        if isinstance(result, list):
                            print(f"   📊 Returned {len(result)} items")
                        elif isinstance(result, dict) and 'id' in result:
                            print(f"   🆔 ID: {result['id']}")
                        return result
                    except:
                        return response.text
                return True
            else:
                print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
            return False
    
    def test_all_endpoints(self):
        """Test all available endpoints with correct routes"""
        print("🔍 Testing All Available Endpoints")
        print("=" * 60)
        
        # Test authentication endpoints
        print("\n1. Authentication Endpoints:")
        user_info = self.test_endpoint('GET', '/api/auth/me')
        if user_info:
            self.user_id = user_info.get('id')
            print(f"   👤 Current User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', 'Unknown')}")
            print(f"   🏷️  Role: {user_info.get('role', 'Unknown')}")
        
        # Test user endpoints
        print("\n2. User Endpoints:")
        users = self.test_endpoint('GET', '/api/users/')
        if users and isinstance(users, list) and len(users) > 0:
            first_user = users[0]
            user_id = first_user.get('id')
            self.test_endpoint('GET', f'/api/users/{user_id}')
        
        # Test freelancer endpoints
        print("\n3. Freelancer Endpoints:")
        self.test_endpoint('GET', '/api/freelancers/')
        self.test_endpoint('GET', '/api/freelancers/stats')
        self.test_endpoint('GET', '/api/freelancers/pending')
        
        # If we have a freelancer ID, test specific freelancer endpoints
        freelancers = self.test_endpoint('GET', '/api/freelancers/')
        if freelancers and isinstance(freelancers, list) and len(freelancers) > 0:
            freelancer_id = freelancers[0]['id']
            self.test_endpoint('GET', f'/api/freelancers/{freelancer_id}')
            
            # Test freelancer skills (if we're a freelancer)
            if user_info and user_info.get('role') == 'freelancer':
                print("\n4. Freelancer Skills:")
                # First, we need to get available skills or create one
                self.test_endpoint('POST', f'/api/freelancers/{self.user_id}/skills', 
                                 {'skill_id': 1, 'proficiency': 'intermediate'}, 
                                 expected_status=400)  # Might fail if skill doesn't exist
        
        # Test project endpoints
        print("\n5. Project Endpoints:")
        projects = self.test_endpoint('GET', '/api/projects/')
        
        # Test creating a project (if we're a client or admin)
        if user_info and user_info.get('role') in ['client', 'admin']:
            print("\n6. Testing Project Creation:")
            project_data = {
                "title": f"Test Project {random.randint(1000, 9999)}",
                "description": "This is a test project for API testing",
                "budget": 1000.00,
                "deadline": "2024-12-31",
                "project_type": "website"
            }
            self.test_endpoint('POST', '/api/projects/', project_data, expected_status=201)
        
        # Test other endpoints
        print("\n7. Other Endpoints:")
        self.test_endpoint('GET', '/api/invoices/')
        self.test_endpoint('GET', '/api/escrow/')
        self.test_endpoint('GET', '/api/deliverable/freelancer/my-deliverables')
        self.test_endpoint('GET', '/api/reviews/')
        self.test_endpoint('GET', '/api/feedback/test')
        self.test_endpoint('GET', '/api/dashboard/stats')
        self.test_endpoint('GET', '/api/activity/')
        
        # Test search endpoints
        print("\n8. Search Endpoints:")
        self.test_endpoint('GET', '/api/freelancers/search', {'skills': 'design'})
        
        print("\n" + "=" * 60)
        print("🎉 All endpoint testing completed!")

def main():
    tester = APITester()
    
    if tester.register_and_login():
        tester.test_all_endpoints()
    else:
        print("❌ Cannot proceed without authentication")

if __name__ == "__main__":
    main()
