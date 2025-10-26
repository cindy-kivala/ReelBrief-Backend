# test_cindy_fixed.py
"""
Fixed test script using correct endpoints and existing deliverable IDs
"""

import requests
from app import create_app, db
from app.models import Deliverable

BASE_URL = "http://localhost:5000"

def get_test_deliverable():
    """Get an actual deliverable ID from the database"""
    app = create_app()
    with app.app_context():
        deliverable = Deliverable.query.first()
        return deliverable.id if deliverable else None

def test_cindy_system():
    print("🚀 Testing Cindy's Deliverables & Feedback System")
    print("=" * 60)
    
    # Get actual deliverable ID
    deliverable_id = get_test_deliverable()
    if not deliverable_id:
        print("❌ No deliverables found in database")
        return
    
    print(f"🎯 Using deliverable ID: {deliverable_id}")
    
    # Login
    print("\n1. 🔐 Logging in test users...")
    
    freelancer_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "cindy_freelancer@example.com",
        "password": "freelancer123"
    })
    
    client_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "cindy_client@example.com",
        "password": "client123"
    })
    
    if freelancer_response.status_code != 200 or client_response.status_code != 200:
        print("❌ Login failed")
        return
    
    freelancer_headers = {"Authorization": f"Bearer {freelancer_response.json()['access_token']}"}
    client_headers = {"Authorization": f"Bearer {client_response.json()['access_token']}"}
    
    print("✅ Both users logged in")
    
    # Test 1: Get deliverables for project
    print("\n2. 📦 Testing GET /api/deliverables/projects/3")
    response = requests.get(f"{BASE_URL}/api/deliverables/projects/3", headers=freelancer_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {len(data.get('deliverables', []))} deliverables")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 2: Get specific deliverable
    print(f"\n3. 📄 Testing GET /api/deliverables/{deliverable_id}")
    response = requests.get(f"{BASE_URL}/api/deliverables/{deliverable_id}", headers=freelancer_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Deliverable retrieved successfully")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 3: Create feedback
    print(f"\n4. 💬 Testing POST /api/feedback/")
    feedback_data = {
        "deliverable_id": deliverable_id,
        "content": "This looks great! Just a few minor adjustments needed on the color scheme.",
        "feedback_type": "revision",
        "priority": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/api/feedback/", json=feedback_data, headers=client_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        feedback = response.json()
        feedback_id = feedback['feedback'].get('id')
        print(f"   ✅ Feedback created with ID: {feedback_id}")
        
        # Test 4: Get feedback for deliverable
        print(f"\n5. 📋 Testing GET /api/feedback/deliverables/{deliverable_id}")
        response = requests.get(f"{BASE_URL}/api/feedback/deliverables/{deliverable_id}", headers=freelancer_headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data.get('total_count', 0)} feedback items")
        
        # Test 5: Resolve feedback
        print(f"\n6. ✔️  Testing PATCH /api/feedback/{feedback_id}/resolve")
        response = requests.patch(f"{BASE_URL}/api/feedback/{feedback_id}/resolve", headers=client_headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Feedback resolved")
        else:
            print(f"   ❌ Error: {response.text}")
    
    else:
        print(f"   ❌ Error creating feedback: {response.text}")
    
    # Test 6: Approve deliverable
    print(f"\n7. ✅ Testing POST /api/deliverables/{deliverable_id}/approve")
    response = requests.post(f"{BASE_URL}/api/deliverables/{deliverable_id}/approve", headers=client_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Deliverable approved")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 7: Request revision
    print(f"\n8. 🔄 Testing POST /api/deliverables/{deliverable_id}/request-revision")
    revision_data = {
        "content": "Please update the header section to match the brand guidelines",
        "priority": "high"
    }
    response = requests.post(
        f"{BASE_URL}/api/deliverables/{deliverable_id}/request-revision",
        json=revision_data,
        headers=client_headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   ✅ Revision requested")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 8: Get feedback stats
    print(f"\n9. 📊 Testing GET /api/feedback/stats/{deliverable_id}")
    response = requests.get(f"{BASE_URL}/api/feedback/stats/{deliverable_id}", headers=freelancer_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json().get('stats', {})
        print(f"   ✅ Stats retrieved:")
        print(f"      - Total feedback: {stats.get('total_feedback', 0)}")
        print(f"      - Unresolved: {stats.get('unresolved_count', 0)}")
        print(f"      - Resolved: {stats.get('resolved_count', 0)}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE!")
    print("=" * 60)
    print("\n✅ Features Tested:")
    print("   • List deliverables by project")
    print("   • Get specific deliverable")
    print("   • Create feedback")
    print("   • Get deliverable feedback")
    print("   • Resolve feedback")
    print("   • Approve deliverable")
    print("   • Request revision")
    print("   • Get feedback statistics")

if __name__ == "__main__":
    test_cindy_system()