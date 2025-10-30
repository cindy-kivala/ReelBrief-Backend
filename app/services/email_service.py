"""
Email Service
Owner: Ryan (final)
Description: Centralized outbound email (verification, password reset, project/deliverable notifications)
Uses SendGrid via app.extensions.sg
"""

import os
from itsdangerous import URLSafeTimedSerializer
from sendgrid.helpers.mail import From, Mail
from flask import current_app

from app.extensions import sg

FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "michenicaleb@gmail.com")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5174")
SECRET_KEY = os.getenv("SECRET_KEY", "devsecretkey")


def create_verification_token(user_id: int, expiration: int = 3600) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(user_id, salt="email-verify")


def send_email(recipient: str, subject: str, html_content: str, from_name: str = FROM_NAME) -> bool:
    if sg is None:
        current_app.logger.error("SendGrid not configured (missing/invalid API key).")
        return False

    message = Mail(
        from_email=From(FROM_EMAIL, from_name),
        to_emails=recipient,
        subject=subject,
        html_content=html_content,
    )
    try:
        response = sg.send(message)
        status = response.status_code
        current_app.logger.info(f"Email to {recipient} | Status: {status}")
        if status not in (200, 202):
            current_app.logger.warning(f"SendGrid non-2xx ({status}): {getattr(response, 'body', '')}")
        return status in (200, 202)
    except Exception as e:
        current_app.logger.error(f"SendGrid send failed: {e}")
        current_app.logger.error(
            "SendGrid failed. Check:\n"
            "- SENDGRID_API_KEY is correct (no quotes/trailing spaces)\n"
            "- API key has 'Mail Send' permission\n"
            "- SENDGRID_FROM_EMAIL is a verified Single Sender/domain"
        )
        return False


def send_verification_email(email: str, user_id: int):
    token = create_verification_token(user_id)
    verify_link = f"{BASE_URL}/verify-email/{token}"

    # html_content = (
    #     f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;'>"
    #     "<h3 style='color: #27ae60;'>Welcome to ReelBrief!</h3>"
    #     f"<p>Hello <strong>{email}</strong>,</p>"
    #     "<p>Please verify your email address to complete registration:</p>"
    #     f"<a href='{verify_link}' style='background:#27ae60; color:white; padding:12px 24px; "
    #     "text-decoration:none; border-radius:5px; display:inline-block;'>"
    #     "Verify Email Address</a>"
    #     "<p><small>This link expires in <strong>1 hour</strong>.</small></p>"
    #     "</div>"
    # )

    # return send_email(email, "Verify Your ReelBrief Email Address", html_content)

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color:#17545B; font-weight:600; margin-bottom:16px;">Welcome to ReelBrief</h2>
        <p style="font-size:15px; color:#333;">Hello <strong>{email}</strong>,</p>
        <p style="font-size:15px; color:#333; line-height:1.5;">Please verify your email to activate your account.</p>
        <p style="margin:24px 0;">
            <a href="{verify_link}" style="background:#17545B;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-size:15px;font-weight:500;display:inline-block;">Verify Email Address</a>
        </p>
        <p style="font-size:12px; color:#777;">This link expires in <strong>1 hour</strong>.</p>
    </div>
    """

    ok = send_email(email, "Verify Your ReelBrief Email Address", html)
    current_app.logger.info(f"Verification link for {email}: {verify_link}")
    return ok, token


def send_password_reset_email(user) -> bool:
    reset_link = f"{BASE_URL}/reset-password/{user.reset_token}"
    display_name = getattr(
        user, "name",
        f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip() or "there"
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#2c3e50; font-weight:600;">Password Reset</h3>
        <p style="font-size:15px; color:#333;">Hi <strong>{display_name}</strong>, click below to reset your password.</p>
        <p style="margin:24px 0;">
            <a href="{reset_link}" style="background:#3498db;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-size:15px;font-weight:500;display:inline-block;">Reset Password</a>
        </p>
        <p style="font-size:12px; color:#777;">This link expires in <strong>30 minutes</strong>.</p>
    </div>
    """
    return send_email(user.email, "Reset Your ReelBrief Password", html)


# (Kept for imports elsewhere)
def send_project_assignment_email(project, freelancer) -> bool:
    project_link = f"{BASE_URL}/projects/{project.id}"
    name = getattr(freelancer, 'name', f"{getattr(freelancer, 'first_name', '')} {getattr(freelancer, 'last_name', '')}".strip() or "there")
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">New Project Assigned!</h3>
        <p>Hi <strong>{name}</strong>, you've been assigned to:</p>
        <h2 style="color:#2c3e50;">{project.title}</h2>
        <p><a href="{project_link}" style="color:#3498db;">View Project →</a></p>
    </div>
    """
    return send_email(freelancer.email, f"New Project: {project.title}", html, from_name="ReelBrief Assignments")


def send_payment_notification(transaction) -> bool:
    amount = f"${float(transaction.amount):.2f}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#f39c12;">Payment Processed</h3>
        <p>Hello <strong>{getattr(transaction.user, 'first_name', 'there')}</strong>,</p>
        <p>Payment of <strong>{amount}</strong> processed.</p>
        <p><strong>ID:</strong> {transaction.id}</p>
    </div>
    """
    return send_email(transaction.user.email, "Payment Confirmation", html)


def send_deliverable_approved_notification(deliverable, freelancer) -> bool:
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"
    name = getattr(freelancer, 'name', f"{getattr(freelancer, 'first_name', '')} {getattr(freelancer, 'last_name', '')}".strip() or "there")
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">Deliverable Approved!</h3>
        <p>Hi <strong>{name}</strong>, your deliverable was approved.</p>
        <h4>{deliverable.title}</h4>
        <p>
            <a href="{deliverable_link}" style="color:#27ae60; font-weight:bold;">View Deliverable →</a>
            &nbsp;|&nbsp;
            <a href="{project_link}" style="color:#3498db;">View Project →</a>
        </p>
        <p>Payment will be released shortly.</p>
    </div>
    """
    return send_email(freelancer.email, f"Deliverable Approved: {deliverable.title}", html, from_name="ReelBrief Notifications")


def send_deliverable_feedback_notification(deliverable, feedback, client) -> bool:
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"
    status = "Revision requested" if getattr(feedback, "is_revision_request", False) else "Feedback received"
    color = "#e67e22" if getattr(feedback, "is_revision_request", False) else "#3498db"
    freelancer_email = getattr(deliverable, "freelancer_email", None) or getattr(feedback.user, "email", None) or getattr(client, "email", None)

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:{color};">Deliverable {status}!</h3>
        <p>The client has left feedback on <strong>{deliverable.title}</strong>:</p>
        <blockquote style="background:#f8f9fa; padding:12px; border-left:4px solid {color}; margin:16px 0;">
            "{getattr(feedback, 'comment', '')}"
        </blockquote>
        <p>
            <a href="{deliverable_link}" style="color:{color}; font-weight:bold;">View Deliverable →</a>
            &nbsp;|&nbsp;
            <a href="{project_link}" style="color:#3498db;">View Project →</a>
        </p>
    </div>
    """

#     subject = f"Feedback: {deliverable.title} – {'Revision Needed' if feedback.is_revision_request else 'Review'}"
#     return send_email(feedback.user.email, subject, html_content, from_name="ReelBrief Feedback")
    to_email = freelancer_email or getattr(client, "email", None)
    if not to_email:
        current_app.logger.warning(" No recipient email for deliverable feedback notification.")
        return False
    return send_email(to_email, f"Feedback: {deliverable.title}", html, from_name="ReelBrief Feedback")

