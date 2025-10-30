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
        """Register a new user and login"""
        test_id = random.randint(1000, 9999)
        user_data = {
            "username": f"testuser{test_id}",
            "email": f"test{test_id}@reelbrief.com", 
            "password": "testpassword123",
            "role": "freelancer",
            "name": f"Test User {test_id}"
        }
        
        print(f"📝 Registering user: {user_data['email']}")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.token = data.get('token')
            if self.token:
                self.headers = {'Authorization': f'Bearer {self.token}'}
                print("✅ Registration and login successful!")
                return True
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
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
        self.test_endpoint('GET', '/api/auth/me')
        self.test_endpoint('POST', '/api/auth/refresh', expected_status=401)  # Might need refresh token
        
        # Test user endpoints
        print("\n2. User Endpoints:")
        users = self.test_endpoint('GET', '/api/users/')
        if users and isinstance(users, list) and len(users) > 0:
            self.user_id = users[0]['id']
            self.test_endpoint('GET', f'/api/users/{self.user_id}')
        
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
            
            # Test freelancer skills
            print("\n4. Freelancer Skills:")
            self.test_endpoint('POST', f'/api/freelancers/{freelancer_id}/skills', 
                             {'skill_id': 1, 'proficiency': 'intermediate'}, 
                             expected_status=201)  # Might fail if skill doesn't exist
        
        # Test project endpoints
        print("\n5. Project Endpoints:")
        self.test_endpoint('GET', '/api/projects/')
        
        # Test skill-related endpoints (we need to check if skills endpoint exists)
        print("\n6. Testing Skill Operations:")
        # Since there's no direct /api/skills endpoint, test through freelancers
        self.test_endpoint('GET', '/api/freelancers/search', 
                          {'skills': 'design'}, 
                          expected_status=200)
        
        # Test other endpoints
        print("\n7. Other Endpoints:")
        self.test_endpoint('GET', '/api/invoices/')
        self.test_endpoint('GET', '/api/escrow/')
        self.test_endpoint('GET', '/api/deliverable/freelancer/my-deliverables')
        self.test_endpoint('GET', '/api/reviews/')
        self.test_endpoint('GET', '/api/feedback/test')
        self.test_endpoint('GET', '/api/dashboard/stats')
        self.test_endpoint('GET', '/api/activity/')
        
        # Test creating a project
        print("\n8. Testing Project Creation:")
        project_data = {
            "title": f"Test Project {random.randint(1000, 9999)}",
            "description": "This is a test project",
            "budget": 1000.00,
            "deadline": "2024-12-31",
            "project_type": "website"
        }
        self.test_endpoint('POST', '/api/projects/', project_data, expected_status=201)
        
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
