"""
Decorators Utility
Owner: Ryan
Description: Contains custom Flask decorators for permissions and access control.
"""

"""
Decorators Utility
Owner: Ryan
Description: Contains custom Flask decorators for permissions, access control, and global exception handling.
"""

"""
Decorators Utility
Owner: Ryan
Description: Contains custom Flask decorators for permissions and access control.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
import traceback


# -------------------- ADMIN ONLY --------------------
def admin_required(fn):
    """
    Restrict route access to admin users.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# -------------------- ROLE RESTRICTED --------------------
def role_required(roles):
    """
    Restrict route access to specific user roles.
    Example usage:
        @role_required(["admin", "client"])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role not in roles:
                return jsonify({"error": "Access denied for your role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# -------------------- GLOBAL EXCEPTION HANDLER --------------------
def handle_exceptions(fn):
    """
    Global exception handling decorator for Flask routes.
    Returns clean JSON error responses instead of crashing.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print("❌ Exception in route:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500
    return wrapper




# TODO: Ryan - Implement decorators
#
# Required functions:
#
# def admin_required(fn):
#     """Restrict route access to admin users."""
#
# def role_required(roles):
#     """Restrict route to specific user roles."""
#
# def handle_exceptions(fn):
#     """Global exception handling decorator."""
