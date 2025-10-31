"""
Decorators Utility
Owner: Ryan
Description: Contains custom Flask decorators for permissions, access control, and global exception handling.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
import traceback


# -------------------- ADMIN ONLY --------------------
def admin_required(fn):
    """
    Restrict route access to admin users.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# -------------------- ROLE RESTRICTED --------------------
def role_required(*roles):
    """Decorator to require specific user roles"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                # Handle both dict and int identity formats
                if isinstance(current_user_id, dict):
                    user_id = current_user_id.get('id')
                else:
                    user_id = current_user_id
                
                user = User.query.get(user_id)
                if not user:
                    return jsonify({"error": "User not found"}), 404
                
                user_role = user.role
                
                # Convert single role to list for consistent handling
                required_roles = list(roles) if roles else []
                
                if user_role not in required_roles:
                    # Safely format the error message
                    role_display = ', '.join(required_roles) if isinstance(required_roles, (list, tuple)) else str(required_roles)
                    return jsonify({
                        "error": "Access denied",
                        "message": f"Requires role(s): {role_display}"
                    }), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({"error": "Authorization failed", "message": str(e)}), 500
        
        return wrapper
    return decorator
# -------------------- ADMIN SHORTCUT --------------------
def admin_required(fn):
    """Restrict route access to admin users only (shortcut)."""
    return role_required("admin")(fn)


# -------------------- GLOBAL EXCEPTION HANDLER --------------------
def handle_exceptions(fn):
    """
    Decorator to catch unexpected exceptions and return a JSON response.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print("❌ Exception in route:", traceback.format_exc())
            return jsonify({
                "error": "An unexpected error occurred.",
                "details": str(e)
            }), 500
    return wrapper
