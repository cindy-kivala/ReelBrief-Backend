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
    """
    Restrict route access to specific user roles.

    Example usage:
        @role_required("admin", "client")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):  # ✅ use 'wrapper' consistently
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # ✅ define user_role properly
            user_role = user.role if user else None

            if user_role not in roles:
                return (
                    jsonify({
                        "error": "Access denied",
                        "message": f"Requires role(s): {', '.join(roles)}"
                    }),
                    403,
                )
            return fn(*args, **kwargs)
        return wrapper  # ✅ return 'wrapper', not undefined 'wrapper' or 'decorated_function'

    return decorator  # ✅ return the actual decorator, not 'wrapper'


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
