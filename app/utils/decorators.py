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

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import traceback

# ------------------------------------------------------
# ROLE-BASED ACCESS CONTROL
# ------------------------------------------------------

def role_required(*roles):
    """
    Restrict route access to specific user roles.

    Usage:
        @role_required("admin")
        @role_required("client", "freelancer")
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in roles:
                return jsonify({
                    "error": "Access denied",
                    "message": f"Requires role(s): {', '.join(roles)}"
                }), 403

            return fn(*args, **kwargs)
        return decorated_function
    return wrapper


def admin_required(fn):
    """
    Restrict route access to admin users only.
    Shortcut for @role_required("admin").
    """
    return role_required("admin")(fn)


# ------------------------------------------------------
# GLOBAL EXCEPTION HANDLER
# ------------------------------------------------------

def handle_exceptions(fn):
    """
    Decorator to catch unexpected exceptions and return a JSON response
    instead of breaking the server.

    Usage:
        @handle_exceptions
        def route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "error": "Server Error",
                "message": str(e)
            }), 500
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
