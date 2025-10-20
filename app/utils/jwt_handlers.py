"""
JWT Error Handlers
Owner: Ryan
Description: Custom handlers for JWT-related errors and edge cases.
"""

from flask import jsonify

def register_jwt_error_handlers(jwt):
    """
    Registers custom error handlers for JWT issues like expired, invalid,
    or missing tokens. Call this after initializing JWTManager(app).
    """

    @jwt.unauthorized_loader
    def handle_missing_token(error):
        return jsonify({
            "error": "Authorization required",
            "message": "Missing or invalid JWT. Please log in again."
        }), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        return jsonify({
            "error": "Invalid token",
            "message": "The provided token is malformed or invalid."
        }), 422

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token expired",
            "message": "Your session has expired. Please log in again."
        }), 401

    @jwt.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token revoked",
            "message": "This token has been revoked."
        }), 401

    @jwt.needs_fresh_token_loader
    def handle_fresh_token_required(jwt_header, jwt_payload):
        return jsonify({
            "error": "Fresh token required",
            "message": "Please reauthenticate to continue."
        }), 401
