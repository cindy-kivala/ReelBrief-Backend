"""
Email Service
Owner: Ryan (updated)
Description: Sends templated emails via SendGrid using app.extensions.sg
"""

import os
from itsdangerous import URLSafeTimedSerializer

from sendgrid.helpers.mail import From, Mail

from app.extensions import sg


FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "michenicaleb@gmail.com")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")


def create_verification_token(user_id: int, expiration: int = 3600) -> str:
    """Create a timed verification token."""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(user_id, salt='email-verify')


def send_email(recipient, subject, html_content, from_name=FROM_NAME):
    """Generic SendGrid email sender."""
    message = Mail(
        from_email=From(FROM_EMAIL, from_name),
        to_emails=recipient,
        subject=subject,
        html_content=html_content,
    )

    try:
        response = sg.send(message)
        status = response.status_code
        print(f"Email sent to {recipient} | Status: {status}")
        if status not in [200, 202]:
            print(f"SendGrid Warn: {status} | {response.body}")
        return True
    except Exception as e:
        print(f"Send email failed: {e}")
        return False


def send_verification_email(email: str, user_id: int):
    """Send email verification link."""
    token = create_verification_token(user_id)
    verify_link = f"{BASE_URL}/verify-email/{token}"
    
    html_content = (
        f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;'>"
        "<h3 style='color: #27ae60;'>Welcome to ReelBrief!</h3>"
        f"<p>Hello <strong>{email}</strong>,</p>"
        "<p>Please verify your email address to complete registration:</p>"
        f"<a href='{verify_link}' style='background:#27ae60; color:white; padding:12px 24px; "
        "text-decoration:none; border-radius:5px; display:inline-block;'>"
        "Verify Email Address</a>"
        "<p><small>This link expires in <strong>1 hour</strong>.</small></p>"
        "</div>"
    )
    
    return send_email(
        email, 
        "Verify Your ReelBrief Email Address", 
        html_content
    )


def send_password_reset_email(user):
    """Send password reset link."""
    reset_link = f"{BASE_URL}/reset-password/{user.reset_token}"
    html_content = (
        f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;'>"
        "<h3 style='color: #2c3e50;'>Password Reset</h3>"
        f"<p>Hello <strong>{user.name}</strong>,</p>"
        "<p>Click below to reset your password:</p>"
        f"<a href='{reset_link}' style='background:#3498db; color:white; padding:12px 24px; "
        "text-decoration:none; border-radius:5px; display:inline-block;'>"
        "Reset Password</a>"
        "<p><small>Link expires in <strong>30 minutes</strong>.</small></p>"
        "</div>"
    )
    return send_email(user.email, "Reset Your ReelBrief Password", html_content)


def send_project_assignment_email(project, freelancer):
    """Notify freelancer of new project."""
    project_link = f"{BASE_URL}/projects/{project.id}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color: #27ae60;">New Project Assigned!</h3>
        <p>Hi <strong>{freelancer.name}</strong>,</p>
        <p>You've been assigned to:</p>
        <h2 style="color: #2c3e50;">{project.title}</h2>
        <p><a href="{project_link}" style="color:#3498db;">View Project →</a></p>
    </div>
    """
    return send_email(
        freelancer.email,
        f"New Project: {project.title}",
        html_content,
        from_name="ReelBrief Assignments",
    )


def send_payment_notification(transaction):
    """Notify user of payment."""
    amount = f"${float(transaction.amount):.2f}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color: #f39c12;">Payment Processed</h3>
        <p>Hello <strong>{transaction.user.name}</strong>,</p>
        <p>Payment of <strong>{amount}</strong> processed.</p>
        <p><strong>ID:</strong> {transaction.id}</p>
    </div>
    """
    return send_email(transaction.user.email, "Payment Confirmation", html_content)


def send_deliverable_approved_notification(deliverable, freelancer):
    """Notify freelancer that their deliverable was approved."""
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color: #27ae60;">Deliverable Approved!</h3>
        <p>Hi <strong>{freelancer.name}</strong>,</p>
        <p>Great news! Your deliverable has been <strong>approved</strong>.</p>
        <h4>{deliverable.title}</h4>
        <p>
            <a href="{deliverable_link}" style="color:#27ae60; font-weight:bold;">View Deliverable →</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="{project_link}" style="color:#3498db;">View Project →</a>
        </p>
        <p>Payment will be released shortly.</p>
    </div>
    """
    return send_email(
        freelancer.email,
        f"Deliverable Approved: {deliverable.title}",
        html_content,
        from_name="ReelBrief Reviews"
    )
# ... [all previous functions] ...

def send_deliverable_feedback_notification(deliverable, feedback, client):
    """Notify freelancer when client leaves feedback or requests revision."""
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"

    status = "revision requested" if feedback.is_revision_request else "feedback received"
    color = "#e67e22" if feedback.is_revision_request else "#3498db"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color: {color};">Deliverable {status.title()}!</h3>
        <p>Hi <strong>{feedback.user.name}</strong>,</p>
        <p>The client has left feedback on your deliverable:</p>
        <h4>{deliverable.title}</h4>
        <blockquote style="background:#f8f9fa; padding:12px; border-left:4px solid {color}; margin:16px 0;">
            "{feedback.comment}"
        </blockquote>
        {f"<p><strong>Revision requested.</strong> Please update and resubmit.</p>" if feedback.is_revision_request else ""}
        <p>
            <a href="{deliverable_link}" style="color:{color}; font-weight:bold;">View Deliverable →</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="{project_link}" style="color:#3498db;">View Project →</a>
        </p>
    </div>
    """
    subject = f"Feedback: {deliverable.title} – {'Revision Needed' if feedback.is_revision_request else 'Review'}"
    return send_email(
        feedback.user.email,
        subject,
        html_content,
        from_name="ReelBrief Feedback"
    )