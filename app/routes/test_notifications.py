# routes/test_notifications.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.services.email_service import (
    send_email, 
    send_verification_email, 
    send_password_reset_email,
    send_project_assignment_email,
    send_payment_notification,
    send_deliverable_approved_notification,
    send_deliverable_feedback_notification,
    send_login_notification_email,
    send_confirmation_email,
    send_invoice_email,
    send_payment_received_email,
    send_funds_released_email,
    send_refund_email,
    send_admin_freelancer_application_email
)

test_bp = Blueprint("test_bp", __name__)


@test_bp.route("/test/notification", methods=["POST"])
@jwt_required()
def test_notification():
    """Test endpoint to create a sample notification - FIXED VERSION"""
    # Ensure we're handling JSON
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 415
        
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    notification_type = data.get("type", "test")

    notification = Notification(
        user_id=current_user_id,
        type=notification_type,
        title="Test Notification",
        message="This is a test notification to verify the system is working.",
        is_emailed=False,
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Test notification created", 
        "notification": notification.to_dict()
    }), 201


@test_bp.route("/test/email", methods=["POST"])
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
        """,
    )

    return jsonify(
        {
            "message": "Test email sent" if success else "Failed to send test email",
            "success": success,
            "recipient": user.email,
        }
    ), (200 if success else 500)


@test_bp.route("/test/notifications/bulk", methods=["POST"])
@jwt_required()
def test_bulk_notifications():
    """Create multiple test notifications"""
    current_user_id = get_jwt_identity()

    notifications_data = [
        {
            "type": "project_assigned",
            "title": "New Project Assignment",
            "message": "You've been assigned to project 'Website Redesign'",
        },
        {
            "type": "payment_received",
            "title": "Payment Processed",
            "message": "Your payment of $500 has been processed",
        },
        {
            "type": "deliverable_approved",
            "title": "Deliverable Approved",
            "message": "Your deliverable 'Homepage Design' was approved",
        },
        {
            "type": "feedback_received",
            "title": "Feedback Received",
            "message": "Client left feedback on your deliverable",
        },
    ]

    created_notifications = []

    for notif_data in notifications_data:
        notification = Notification(
            user_id=current_user_id,
            type=notif_data["type"],
            title=notif_data["title"],
            message=notif_data["message"],
            is_emailed=False,
        )
        db.session.add(notification)
        created_notifications.append(notification.to_dict())

    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Created {len(created_notifications)} test notifications",
                "notifications": created_notifications,
            }
        ),
        201,
    )

@test_bp.route("/test/email/all", methods=["POST"])
@jwt_required()
def test_all_emails():
    """Test all email types"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    test_results = {}
    
    # Test verification email
    success, token = send_verification_email(user.email, user.id)
    test_results["verification_email"] = success
    
    # Test welcome email
    test_results["welcome_email"] = send_confirmation_email(user)
    
    # Test login notification
    test_results["login_notification"] = send_login_notification_email(user)
    
    # Test password reset (mock token)
    user.reset_token = "test_reset_token_123"
    test_results["password_reset"] = send_password_reset_email(user)
    
    return jsonify({
        "message": "Email tests completed",
        "results": test_results,
        "user_email": user.email
    }), 200