# routes/test_notifications.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.services.email_service import send_email

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/test/notification', methods=['POST'])
@jwt_required()
def test_notification():
    """Test endpoint to create a sample notification"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json() or {}
    notification_type = data.get('type', 'test')
    
    notification = Notification(
        user_id=current_user_id,
        type=notification_type,
        title="Test Notification",
        message="This is a test notification to verify the system is working.",
        is_emailed=False
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        "message": "Test notification created",
        "notification": notification.to_dict()
    }), 201

@test_bp.route('/test/email', methods=['POST'])
@jwt_required()
def test_email():
    """Test endpoint to send a sample email"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    success = send_email(
        recipient=user.email,
        subject="Test Email from ReelBrief",
        html_content="""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color:#17545B;">Test Email</h2>
            <p>This is a test email to verify the email system is working.</p>
            <p>If you're receiving this, SendGrid is properly configured!</p>
        </div>
        """
    )
    
    return jsonify({
        "message": "Test email sent" if success else "Failed to send test email",
        "success": success,
        "recipient": user.email
    }), 200 if success else 500

@test_bp.route('/test/notifications/bulk', methods=['POST'])
@jwt_required()
def test_bulk_notifications():
    """Create multiple test notifications"""
    current_user_id = get_jwt_identity()
    
    notifications_data = [
        {
            "type": "project_assigned",
            "title": "New Project Assignment",
            "message": "You've been assigned to project 'Website Redesign'"
        },
        {
            "type": "payment_received", 
            "title": "Payment Processed",
            "message": "Your payment of $500 has been processed"
        },
        {
            "type": "deliverable_approved",
            "title": "Deliverable Approved",
            "message": "Your deliverable 'Homepage Design' was approved"
        },
        {
            "type": "feedback_received",
            "title": "Feedback Received",
            "message": "Client left feedback on your deliverable"
        }
    ]
    
    created_notifications = []
    
    for notif_data in notifications_data:
        notification = Notification(
            user_id=current_user_id,
            type=notif_data["type"],
            title=notif_data["title"],
            message=notif_data["message"],
            is_emailed=False
        )
        db.session.add(notification)
        created_notifications.append(notification.to_dict())
    
    db.session.commit()
    
    return jsonify({
        "message": f"Created {len(created_notifications)} test notifications",
        "notifications": created_notifications
    }), 201