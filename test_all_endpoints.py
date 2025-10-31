#!/usr/bin/env python3
"""
Complete API Test Script for ReelBrief Backend
Tests all endpoints with proper authentication and payloads
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USERS = {
    "admin": {"email": "admin@reelbrief.com", "password": "admin123"},
    "client": {"email": "sarah@techstartup.com", "password": "client123"}, 
    "freelancer": {"email": "alex@designer.com", "password": "freelancer123"}
}

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {}
        self.current_user = None
        self.test_data = {
            "project_id": None,
            "deliverable_id": None,
            "feedback_id": None,
            "review_id": None
        }
    
    def print_result(self, endpoint: str, status_code: int, result: Any, items_count: int = None):
        """Print formatted test result"""
        status_icon = "✅" if status_code in [200, 201] else "❌"
        items_info = f" - {items_count} items" if items_count is not None else ""
        print(f"{status_icon} {endpoint}: {status_code}{items_info}")
        
        if status_code not in [200, 201]:
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"   Error: {result['error']}")
                if 'message' in result:
                    print(f"   Message: {result['message']}")
            else:
                print(f"   Response: {result}")
    
    def login(self, user_type: str) -> bool:
        """Login as specific user type"""
        try:
            user_creds = TEST_USERS[user_type]
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=user_creds
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data.get('access_token')
                self.current_user = user_type
                print(f"🔐 Logged in as {user_type}: {user_creds['email']}")
                return True
            else:
                print(f"❌ Login failed for {user_type}: {response.status_code}")
                if response.content:
                    print(f"   Response: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self, user_type: str = None) -> Dict[str, str]:
        """Get headers with authentication token"""
        user = user_type or self.current_user
        token = self.tokens.get(user)
        if token:
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 TESTING AUTH ENDPOINTS")
        print("=" * 50)
        
        # Test login for all users
        for user_type in TEST_USERS.keys():
            self.login(user_type)
    
    def test_user_endpoints(self):
        """Test user management endpoints"""
        print("\n👤 TESTING USER ENDPOINTS")
        print("=" * 50)
        
        # Get current user profile
        response = requests.get(
            f"{self.base_url}/users/me",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        self.print_result("GET /api/users/me", response.status_code, result)
        
        # Get all users (admin only)
        if self.current_user == 'admin':
            response = requests.get(
                f"{self.base_url}/users/",
                headers=self.get_headers()
            )
            result = response.json() if response.content else {}
            items_count = len(result) if isinstance(result, list) else None
            self.print_result("GET /api/users/", response.status_code, result, items_count)
    
    def test_project_endpoints(self):
        """Test project management endpoints"""
        print("\n📋 TESTING PROJECT ENDPOINTS")
        print("=" * 50)
        
        # Get all projects
        response = requests.get(
            f"{self.base_url}/projects/",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        items_count = len(result) if isinstance(result, list) else None
        self.print_result("GET /api/projects/", response.status_code, result, items_count)
        
        # Try to extract project ID for testing
        if items_count and items_count > 0:
            self.test_data["project_id"] = result[0].get('id')
            print(f"   Using project ID: {self.test_data['project_id']}")
        
        # Create a new project (client only)
        if self.current_user == 'client':
            project_data = {
                "title": "Test Project from API",
                "description": "This is a test project created via API",
                "budget": 1500.00,
                "deadline": "2024-12-31",
                "skills_required": ["design", "ui/ux"],
                "category": "design"
            }
            
            response = requests.post(
                f"{self.base_url}/projects/",
                headers=self.get_headers(),
                json=project_data
            )
            result = response.json() if response.content else {}
            self.print_result("POST /api/projects/", response.status_code, result)
            
            if response.status_code == 201:
                project_data = result.get('project', result)
                self.test_data["project_id"] = project_data.get('id')
                print(f"   Created project ID: {self.test_data['project_id']}")
    
    def test_freelancer_endpoints(self):
        """Test freelancer endpoints"""
        print("\n🎨 TESTING FREELANCER ENDPOINTS")
        print("=" * 50)
        
        # Get all freelancers
        response = requests.get(
            f"{self.base_url}/freelancers/",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        items_count = len(result) if isinstance(result, list) else None
        self.print_result("GET /api/freelancers/", response.status_code, result, items_count)
        
        # Get freelancer profile (for freelancer users)
        if self.current_user == 'freelancer':
            response = requests.get(
                f"{self.base_url}/freelancers/profile",
                headers=self.get_headers()
            )
            result = response.json() if response.content else {}
            self.print_result("GET /api/freelancers/profile", response.status_code, result)
    
    def test_deliverable_endpoints(self):
        """Test deliverable endpoints"""
        print("\n📦 TESTING DELIVERABLE ENDPOINTS")
        print("=" * 50)
        
        # Get freelancer's deliverables
        if self.current_user == 'freelancer':
            response = requests.get(
                f"{self.base_url}/deliverable/freelancer/my-deliverables",
                headers=self.get_headers()
            )
            result = response.json() if response.content else {}
            items_count = len(result) if isinstance(result, list) else None
            self.print_result("GET /api/deliverable/freelancer/my-deliverables", response.status_code, result, items_count)
            
            # Store first deliverable ID for feedback testing
            if items_count and items_count > 0:
                self.test_data["deliverable_id"] = result[0].get('id')
                print(f"   Using deliverable ID: {self.test_data['deliverable_id']}")
        
        # Alternative: Try to get deliverables by project if we have a project ID
        if self.test_data.get("project_id"):
            response = requests.get(
                f"{self.base_url}/deliverable/project/{self.test_data['project_id']}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.json()
                items_count = len(result) if isinstance(result, list) else None
                self.print_result(f"GET /api/deliverable/project/{self.test_data['project_id']}", response.status_code, result, items_count)
                
                if items_count and items_count > 0:
                    self.test_data["deliverable_id"] = result[0].get('id')
                    print(f"   Using deliverable ID: {self.test_data['deliverable_id']}")
    
    def test_feedback_endpoints(self):
        """Test feedback endpoints (deliverable-specific)"""
        print("\n💬 TESTING FEEDBACK ENDPOINTS")
        print("=" * 50)
        
        # Try to get a deliverable ID if we don't have one
        if not self.test_data.get("deliverable_id"):
            print("⚠️  No deliverable ID available - trying to find one...")
            self.test_deliverable_endpoints()
        
        if not self.test_data.get("deliverable_id"):
            print("❌ Skipping feedback tests - no deliverable ID available")
            return
        
        # Submit feedback on deliverable
        feedback_data = {
            "deliverable_id": self.test_data["deliverable_id"],
            "feedback_type": "revision",  # comment, revision, approval
            "content": "This is test feedback via API. Please make the requested changes.",
            "priority": "high"  # low, medium, high
        }
        
        response = requests.post(
            f"{self.base_url}/feedback/",
            headers=self.get_headers(),
            json=feedback_data
        )
        result = response.json() if response.content else {}
        self.print_result("POST /api/feedback/", response.status_code, result)
        
        if response.status_code == 201:
            feedback_data = result.get('feedback', result)
            self.test_data["feedback_id"] = feedback_data.get('id')
            print(f"   Created feedback ID: {self.test_data['feedback_id']}")
        
        # Get feedback for deliverable
        response = requests.get(
            f"{self.base_url}/feedback/deliverable/{self.test_data['deliverable_id']}",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        if isinstance(result, dict) and 'feedback' in result:
            items_count = len(result['feedback'])
        else:
            items_count = len(result) if isinstance(result, list) else None
        self.print_result(f"GET /api/feedback/deliverable/{self.test_data['deliverable_id']}", response.status_code, result, items_count)
    
    def test_review_endpoints(self):
        """Test review endpoints (project ratings)"""
        print("\n⭐ TESTING REVIEW ENDPOINTS")
        print("=" * 50)
        
        # Try to get a project ID if we don't have one
        if not self.test_data.get("project_id"):
            print("⚠️  No project ID available - trying to find one...")
            self.test_project_endpoints()
        
        if not self.test_data.get("project_id"):
            print("❌ Skipping review tests - no project ID available")
            return
        
        # Submit review for project (client only)
        if self.current_user == 'client':
            review_data = {
                "project_id": self.test_data["project_id"],
                "rating": 5,  # Required: 1-5
                "review_text": "Excellent work on the test project! Very professional and delivered on time.",
                "communication_rating": 5,  # Optional: 1-5
                "quality_rating": 5,        # Optional: 1-5
                "timeliness_rating": 4,     # Optional: 1-5
                "is_public": True
            }
            
            response = requests.post(
                f"{self.base_url}/reviews/",
                headers=self.get_headers(),
                json=review_data
            )
            result = response.json() if response.content else {}
            self.print_result("POST /api/reviews/", response.status_code, result)
            
            if response.status_code == 201:
                review_data = result.get('review', result)
                self.test_data["review_id"] = review_data.get('id')
                print(f"   Created review ID: {self.test_data['review_id']}")
        
        # Get project review
        response = requests.get(
            f"{self.base_url}/reviews/project/{self.test_data['project_id']}",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        self.print_result(f"GET /api/reviews/project/{self.test_data['project_id']}", response.status_code, result)
        
        # Get user's reviews
        response = requests.get(
            f"{self.base_url}/reviews/user/my-reviews",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        self.print_result("GET /api/reviews/user/my-reviews", response.status_code, result)
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n📊 TESTING DASHBOARD ENDPOINTS")
        print("=" * 50)
        
        # Get dashboard stats
        response = requests.get(
            f"{self.base_url}/dashboard/stats",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        self.print_result("GET /api/dashboard/stats", response.status_code, result)
        
        # Get dashboard activity
        response = requests.get(
            f"{self.base_url}/dashboard/activity",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        items_count = len(result) if isinstance(result, list) else None
        self.print_result("GET /api/dashboard/activity", response.status_code, result, items_count)
    
    def test_escrow_endpoints(self):
        """Test escrow endpoints"""
        print("\n💰 TESTING ESCROW ENDPOINTS")
        print("=" * 50)
        
        response = requests.get(
            f"{self.base_url}/escrow/",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        items_count = len(result) if isinstance(result, list) else None
        self.print_result("GET /api/escrow/", response.status_code, result, items_count)
    
    def test_invoice_endpoints(self):
        """Test invoice endpoints"""
        print("\n🧾 TESTING INVOICE ENDPOINTS")
        print("=" * 50)
        
        response = requests.get(
            f"{self.base_url}/invoices/",
            headers=self.get_headers()
        )
        result = response.json() if response.content else {}
        items_count = len(result) if isinstance(result, list) else None
        self.print_result("GET /api/invoices/", response.status_code, result, items_count)
    
    def run_comprehensive_test(self):
        """Run comprehensive tests for all user types"""
        print("🚀 STARTING COMPREHENSIVE API TESTS")
        print("=" * 60)
        
        user_types = ['admin', 'client', 'freelancer']
        
        for user_type in user_types:
            print(f"\n{'='*60}")
            print(f"👤 TESTING AS {user_type.upper()}")
            print(f"{'='*60}")
            
            # Login as current user type
            if not self.login(user_type):
                continue
            
            # Run tests for this user type
            self.test_auth_endpoints()
            self.test_user_endpoints()
            self.test_project_endpoints()
            self.test_freelancer_endpoints()
            self.test_deliverable_endpoints()
            self.test_feedback_endpoints()
            self.test_review_endpoints()
            self.test_dashboard_endpoints()
            self.test_escrow_endpoints()
            self.test_invoice_endpoints()
            
            # Reset test data for next user
            self.test_data = {
                "project_id": None,
                "deliverable_id": None,
                "feedback_id": None,
                "review_id": None
            }
    
    def run_specific_test(self, user_type: str, test_type: str):
        """Run specific test for a user type"""
        print(f"\n🎯 RUNNING SPECIFIC TEST: {test_type.upper()} as {user_type.upper()}")
        print("=" * 60)
        
        if not self.login(user_type):
            return
        
        test_methods = {
            'auth': self.test_auth_endpoints,
            'users': self.test_user_endpoints,
            'projects': self.test_project_endpoints,
            'freelancers': self.test_freelancer_endpoints,
            'deliverables': self.test_deliverable_endpoints,
            'feedback': self.test_feedback_endpoints,
            'reviews': self.test_review_endpoints,
            'dashboard': self.test_dashboard_endpoints,
            'escrow': self.test_escrow_endpoints,
            'invoices': self.test_invoice_endpoints,
            'all': self.run_all_tests_for_current_user
        }
        
        if test_type in test_methods:
            test_methods[test_type]()
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available test types: auth, users, projects, freelancers, deliverables, feedback, reviews, dashboard, escrow, invoices, all")
    
    def run_all_tests_for_current_user(self):
        """Run all tests for the current user"""
        self.test_auth_endpoints()
        self.test_user_endpoints()
        self.test_project_endpoints()
        self.test_freelancer_endpoints()
        self.test_deliverable_endpoints()
        self.test_feedback_endpoints()
        self.test_review_endpoints()
        self.test_dashboard_endpoints()
        self.test_escrow_endpoints()
        self.test_invoice_endpoints()

def main():
    """Main function"""
    tester = APITester()
    
    if len(sys.argv) > 1:
        # Run specific test
        if len(sys.argv) >= 3:
            user_type = sys.argv[1]
            test_type = sys.argv[2]
            tester.run_specific_test(user_type, test_type)
        else:
            print("Usage: python test_all_endpoints.py [user_type] [test_type]")
            print("User types: admin, client, freelancer")
            print("Test types: auth, users, projects, freelancers, deliverables, feedback, reviews, dashboard, escrow, invoices, all")
    else:
        # Run comprehensive test
        tester.run_comprehensive_test()
    
    print("\n" + "="*60)
    print("🎉 TESTING COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()