from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

notification_bp = Blueprint('notification_bp', __name__)

@notification_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get user notification preferences"""
    user_id = get_jwt_identity()
    
    return jsonify({
        "email_notifications": True,
        "project_updates": True,
        "payment_reminders": True,
        "marketing_emails": False
    }), 200

@notification_bp.route('/preferences', methods=['PATCH'])
@jwt_required()
def update_notification_preferences():
    """Update user notification preferences"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    return jsonify({
        "message": "Preferences updated successfully",
        "preferences": data
    }), 200