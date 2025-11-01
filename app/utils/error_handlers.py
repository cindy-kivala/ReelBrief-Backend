"""
Global Error Handlers
Owner: Ryan
Description: Unified error responses for common HTTP and server errors.
"""

from flask import jsonify


def register_error_handlers(app):
    """Attach global error handlers to the Flask app."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": str(e)}), 403

    @app.errorhandler(404)
    def not_found(e):
        return (
            jsonify({"error": "Not Found", "message": "The requested resource was not found."}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method Not Allowed", "message": "Check your HTTP method."}), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return (
            jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}),
            500,
        )
