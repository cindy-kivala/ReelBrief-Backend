#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_with_seeded_users():
    print("🌱 Testing with Seeded Users from seed.py")
    print("=" * 60)
    
    # These are the users from your seed data
    seeded_users = [
        {"email": "cindy@gmail.com", "password": "password123", "role": "client"},
        {"email": "alice@gmail.com", "password": "password123", "role": "freelancer"},
        {"email": "bob@gmail.com", "password": "password123", "role": "freelancer"},
        {"email": "carol@gmail.com", "password": "password123", "role": "freelancer"},
    ]
    
    token = None
    user_info = None
    successful_login = None
    
    print("🔐 Trying seeded user logins:")
    print("-" * 40)
    
    for user in seeded_users:
        print(f"   Trying: {user['email']} ({user['role']})")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                successful_login = user
                print(f"   ✅ SUCCESS! Logged in as {user['email']}")
                
                # Get user info to verify
                headers = {'Authorization': f'Bearer {token}'}
                user_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                if user_resp.status_code == 200:
                    user_info = user_resp.json()
                    print(f"   👤 User Info: {user_info.get('name', 'Unknown')}")
                    print(f"   🆔 User ID: {user_info.get('id')}")
                    print(f"   🏷️  Role: {user_info.get('role')}")
                break
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
    
    if not token:
        print("❌ No seeded users could log in. The database might not be seeded.")
        print("💡 Run: flask db seed")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"\n🎯 Testing API as {successful_login['role'].upper()}")
    print("=" * 50)
    
    # Test basic endpoints
    print("\n1. 📊 Basic Endpoints:")
    basic_endpoints = [
        ('GET', '/api/auth/me'),
        ('GET', '/api/users/'),
        ('GET', '/api/freelancers/'),
        ('GET', '/api/projects/'),
        ('GET', '/api/dashboard/stats'),
    ]
    
    for method, endpoint in basic_endpoints:
        response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers)
        status_icon = "✅" if response.status_code == 200 else "⚠️ "
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   {status_icon} {method} {endpoint} - {len(data)} items")
            else:
                print(f"   {status_icon} {method} {endpoint} - OK")
        else:
            print(f"   {status_icon} {method} {endpoint} - {response.status_code}")
    
    # Role-specific testing
    print(f"\n2. 🎭 {successful_login['role'].upper()}-Specific Endpoints:")
    
    if successful_login['role'] == 'freelancer':
        freelancer_endpoints = [
            ('GET', '/api/freelancers/stats'),
            ('GET', '/api/deliverable/freelancer/my-deliverables'),
            ('GET', '/api/invoices/'),
        ]
        
        for method, endpoint in freelancer_endpoints:
            response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers)
            status_icon = "✅" if response.status_code == 200 else "⚠️ "
            print(f"   {status_icon} {method} {endpoint} - {response.status_code}")
    
    elif successful_login['role'] == 'client':
        client_endpoints = [
            ('GET', '/api/invoices/'),
            ('GET', '/api/escrow/'),
            ('POST', '/api/projects/'),
        ]
        
        for method, endpoint in client_endpoints:
            if method == 'POST':
                # Try to create a project
                project_data = {
                    "title": "Test Project from API",
                    "description": "This is a test project created via API",
                    "budget": 1000.00,
                    "deadline": "2024-12-31",
                    "project_type": "website"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", json=project_data, headers=headers)
            else:
                response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers)
            
            status_icon = "✅" if response.status_code in [200, 201] else "⚠️ "
            print(f"   {status_icon} {method} {endpoint} - {response.status_code}")
    
    # Test freelancer profiles and skills
    print(f"\n3. �� Testing Freelancer Data:")
    
    # Get freelancers list
    freelancers_resp = requests.get(f"{BASE_URL}/api/freelancers/", headers=headers)
    if freelancers_resp.status_code == 200:
        freelancers = freelancers_resp.json()
        print(f"   📋 Found {len(freelancers)} freelancers")
        
        if freelancers:
            # Test getting a specific freelancer
            first_freelancer = freelancers[0]
            freelancer_id = first_freelancer.get('id')
            
            # Get freelancer details
            detail_resp = requests.get(f"{BASE_URL}/api/freelancers/{freelancer_id}", headers=headers)
            if detail_resp.status_code == 200:
                freelancer_detail = detail_resp.json()
                print(f"   👤 Freelancer: {freelancer_detail.get('name', 'Unknown')}")
                print(f"   �� Rate: ${freelancer_detail.get('hourly_rate', 'N/A')}/hr")
                print(f"   📝 Status: {freelancer_detail.get('application_status', 'Unknown')}")
                
                # Check if skills are included
                if 'skills' in freelancer_detail:
                    print(f"   🛠️  Skills: {', '.join(freelancer_detail['skills'])}")
    
    # Test projects
    print(f"\n4. 🚀 Testing Projects:")
    projects_resp = requests.get(f"{BASE_URL}/api/projects/", headers=headers)
    if projects_resp.status_code == 200:
        projects = projects_resp.json()
        print(f"   📋 Found {len(projects)} projects")
        
        for project in projects[:2]:  # Show first 2 projects
            print(f"   📁 Project: {project.get('title', 'Unknown')}")
            print(f"     💰 Budget: ${project.get('budget', 'N/A')}")
            print(f"     📅 Status: {project.get('status', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed with seeded data!")
    print(f"📊 Logged in as: {successful_login['email']} ({successful_login['role']})")

if __name__ == "__main__":
    test_with_seeded_users()
