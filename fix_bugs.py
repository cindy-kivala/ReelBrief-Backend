"""
Quick bug fixes for the identified issues
"""

import os

def fix_decorators_bug():
    """Fix the role_required decorator bug"""
    file_path = "app/utils/decorators.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and replace the problematic line
    old_line = '"message": f"Requires role(s): {\', \'.join(roles)}"'
    new_line = '"message": f"Requires role(s): {\', \'.join(roles) if isinstance(roles, (list, tuple)) else roles}"'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        with open(file_path, 'w') as f:
            f.write(content)
        print("✅ Fixed decorators.py bug")
    else:
        print("⚠️  Could not find the exact line to fix in decorators.py")

def fix_dashboard_bug():
    """Fix the dashboard activity bug"""
    file_path = "app/resources/dashboard_resource.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the get_activity function and fix it
    old_function = '''
@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity():
    user_id = get_jwt_identity()
    role = get_jwt_identity()["role"]

    if role == "admin":
        activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    else:
        activities = (
            ActivityLog.query.filter_by(user_id=user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
            .all()
        )

    return jsonify([activity.to_dict() for activity in activities])
'''
    
    new_function = '''
@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity():
    current_user = get_jwt_identity()
    
    # Handle both identity formats
    if isinstance(current_user, dict):
        user_id = current_user.get('id')
        role = current_user.get('role')
    else:
        # If it's just an ID, get the user from database
        user_id = current_user
        user = User.query.get(user_id)
        role = user.role if user else None
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400

    if role == "admin":
        activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    else:
        activities = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return jsonify([activity.to_dict() for activity in activities])
'''
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        with open(file_path, 'w') as f:
            f.write(content)
        print("✅ Fixed dashboard_resource.py bug")
    else:
        print("⚠️  Could not find the exact function to fix in dashboard_resource.py")

if __name__ == "__main__":
    print("🔧 Applying critical bug fixes...")
    fix_decorators_bug()
    fix_dashboard_bug()
    print("🎉 Fixes applied! Restart your Flask server.")