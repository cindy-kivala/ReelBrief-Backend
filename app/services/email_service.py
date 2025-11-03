# app/services/email_service.py
"""
Email Service
Owner: Ryan (final)
Centralized outbound email (verification, password reset, admin alerts, etc.)
"""

from typing import Tuple, Optional  # 3.8-safe typing
import logging
import os

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from sendgrid.helpers.mail import From, Mail

from app.extensions import sg  # Initialized SendGrid client (or None)

FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "michenicaleb@gmail.com")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")
SECRET_KEY = os.getenv("SECRET_KEY", "devsecretkey")
ADMIN_ALERT_EMAIL = os.getenv("ADMIN_ALERT_EMAIL")

# ---- Logger ----
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# ---- Helpers ----
def _display_name(user) -> str:
    first = getattr(user, "first_name", "") or ""
    last = getattr(user, "last_name", "") or ""
    full = (first + " " + last).strip()
    return full or getattr(user, "name", None) or "there"

# ---- Tokens ----
def create_verification_token(user_id: int, expiration: int = 3600) -> str:
    # Expiration is enforced when loading the token, not here.
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(user_id, salt="email-verify")


def send_email(recipient: str, subject: str, html_content: str, from_name: str = FROM_NAME) -> bool:
    if sg is None:
        current_app.logger.error("SendGrid not configured (missing/invalid API key).")
        return False

    message = Mail(
        from_email=From(FROM_EMAIL, from_name or FROM_NAME),
        to_emails=recipient,
        subject=subject,
        html_content=html_content,
    )

    try:
        response = sg.send(message)
        status = response.status_code
        current_app.logger.info(f"Email to {recipient} | Status: {status}")
        if status not in (200, 202):
            current_app.logger.warning(
                f"SendGrid non-2xx ({status}): {getattr(response, 'body', '')}"
            )
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

# ---- Verification ----
def send_verification_email(email: str, user_id: int) -> Tuple[bool, str]:
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
        <p style="font-size:15px; color:#333; line-height:1.5;">Please verify your email address to activate your account.</p>
        <p style="margin:24px 0;">
            <a href="{verify_link}"
               style="background:#17545B;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-size:15px;font-weight:500;display:inline-block">
               Verify Email Address
            </a>
        </p>
        <p style="font-size:12px; color:#777;">This link expires in <strong>1 hour</strong>.</p>
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
        <p style="font-size:12px;color:#999;">ReelBrief · Creative Collaboration & Payments</p>
    </div>
    """
    ok = send_email(email, "Verify Your ReelBrief Email Address", html)
    current_app.logger.info(f"Verification link for {email}: {verify_link}")
    return ok, token

# ---- Password reset ----
def send_password_reset_email(user) -> bool:
    reset_link = f"{BASE_URL}/reset-password/{user.reset_token}"
    display_name = getattr(
        user,
        "name",
        f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip() or "there",
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#2c3e50; font-weight:600; margin-bottom:16px;">Password Reset</h3>
        <p style="font-size:15px; color:#333;">Hi <strong>{name}</strong>,</p>
        <p style="font-size:15px; color:#333; line-height:1.5;">We received a request to reset your ReelBrief password.</p>
        <p style="margin:24px 0;">
            <a href="{reset_link}"
               style="background:#3498db;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-size:15px;font-weight:500;display:inline-block">
               Reset Password
            </a>
        </p>
        <p style="font-size:12px; color:#777;">This link expires in <strong>30 minutes</strong>.</p>
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
        <p style="font-size:12px;color:#999;">ReelBrief Security</p>
    </div>
    """
    return send_email(getattr(user, "email", ""), "Reset Your ReelBrief Password", html)

# ---- Project assignment ----
def send_project_assignment_email(project, freelancer) -> bool:
    project_link = f"{BASE_URL}/projects/{project.id}"
    name = getattr(
        freelancer,
        "name",
        f"{getattr(freelancer, 'first_name', '')} {getattr(freelancer, 'last_name', '')}".strip()
        or "there",
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">New Project Assigned!</h3>
        <p>Hi <strong>{name}</strong>,</p>
        <p>You've been assigned to:</p>
        <h2 style="color:#2c3e50;">{getattr(project, 'title', 'A Project')}</h2>
        <p><a href="{project_link}" style="color:#3498db;">View Project →</a></p>
    </div>
    """
    return send_email(
        freelancer.email, f"New Project: {project.title}", html, from_name="ReelBrief Assignments"
    )


# ---- Payment notification ----
def send_payment_notification(transaction) -> bool:
    user = getattr(transaction, "user", None)
    if not user:
        LOGGER.error("❌ send_payment_notification called without transaction.user")
        return False
    amount = float(getattr(transaction, "amount", 0.0))
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#f39c12;">Payment Processed</h3>
        <p>Hello <strong>{_display_name(user)}</strong>,</p>
        <p>Payment of <strong>${amount:.2f}</strong> processed.</p>
        <p><strong>ID:</strong> {getattr(transaction, 'id', '')}</p>
    </div>
    """
    return send_email(getattr(user, "email", ""), "Payment Confirmation", html)

# ---- Deliverable approved ----
def send_deliverable_approved_notification(deliverable, freelancer) -> bool:
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"
    name = getattr(
        freelancer,
        "name",
        f"{getattr(freelancer, 'first_name', '')} {getattr(freelancer, 'last_name', '')}".strip()
        or "there",
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">Deliverable Approved!</h3>
        <p>Hi <strong>{_display_name(freelancer)}</strong>,</p>
        <p>Great news! Your deliverable has been <strong>approved</strong>.</p>
        <h4>{getattr(deliverable, 'title', 'Deliverable')}</h4>
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
        html,
        from_name="ReelBrief Notifications",
    )


def send_deliverable_feedback_notification(deliverable, feedback, client) -> bool:
    project_link = f"{BASE_URL}/projects/{deliverable.project_id}"
    deliverable_link = f"{BASE_URL}/deliverables/{deliverable.id}"
    status = (
        "Revision requested"
        if getattr(feedback, "is_revision_request", False)
        else "Feedback received"
    )
    color = "#e67e22" if getattr(feedback, "is_revision_request", False) else "#3498db"
    freelancer_email = (
        getattr(deliverable, "freelancer_email", None)
        or getattr(feedback.user, "email", None)
        or getattr(client, "email", None)
    )

# ---- Deliverable feedback ----
def send_deliverable_feedback_notification(deliverable, feedback, recipient_user) -> bool:
    project_id = getattr(deliverable, "project_id", None)
    project_link = f"{BASE_URL}/projects/{project_id}" if project_id else BASE_URL
    deliverable_link = f"{BASE_URL}/deliverables/{getattr(deliverable, 'id', '')}"
    is_revision = bool(getattr(feedback, "is_revision_request", False))
    status = "revision requested" if is_revision else "feedback received"
    color = "#e67e22" if is_revision else "#3498db"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color: {color};">Deliverable {status.title()}!</h3>
        <p>Hi <strong>{_display_name(recipient_user)}</strong>,</p>
        <p>The client has left feedback on your deliverable:</p>
        <h4>{getattr(deliverable, 'title', 'Deliverable')}</h4>
        <blockquote style="background:#f8f9fa; padding:12px; border-left:4px solid {color}; margin:16px 0;">
            "{getattr(feedback, 'comment', '')}"
        </blockquote>
        {"<p><strong>Revision requested.</strong> Please update and resubmit.</p>" if is_revision else ""}
        <p>
            <a href="{deliverable_link}" style="color:{color}; font-weight:bold;">View Deliverable →</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
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
    return send_email(
        to_email, f"Feedback: {deliverable.title}", html, from_name="ReelBrief Feedback"
    )


def send_login_notification_email(user) -> bool:
    """Send a notification email when a user logs in successfully."""
    from datetime import datetime

    login_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#17545B;">Successful Login</h3>
        <p>Hello <strong>{user.first_name or user.email}</strong>,</p>
        <p>You just logged in to your ReelBrief account on <strong>{login_time}</strong>.</p>
        <p>If this wasn’t you, please reset your password immediately.</p>
        <p style="margin:24px 0;">
            <a href="{BASE_URL}/reset-password" 
               style="background:#c0392b;color:#fff;padding:10px 18px;text-decoration:none;border-radius:6px;">
               Reset Password
            </a>
        </p>
        <p style="font-size:12px; color:#777;">This is an automated message from ReelBrief Security.</p>
    </div>
    """

    return send_email(
        user.email, "Login Alert - ReelBrief Account", html, from_name="ReelBrief Security"
    )


def send_confirmation_email(user):
    """Sends a confirmation email after successful registration."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#17545B;">Welcome to ReelBrief!</h3>
        <p>Hi <strong>{user.first_name}</strong>,</p>
        <p>Thank you for registering with ReelBrief. Your account is now active and ready to use.</p>
        <p>You can log in anytime to start exploring opportunities.</p>
        <br>
        <p style="color:#888;">— The ReelBrief Team</p>
    </div>
    """
    return send_email(
        user.email, "Welcome to ReelBrief!", html, from_name="ReelBrief Notifications"
    )


# ===========================
# 📩  INVOICING + ESCROW EMAILS
# ===========================


def send_invoice_email(invoice, client):
    """Notify client when admin sends an invoice."""
    invoice_link = f"{BASE_URL}/invoices/{invoice.id}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#17545B;">New Invoice Issued</h3>
        <p>Hi <strong>{client.first_name}</strong>,</p>
        <p>An invoice has been issued for <strong>{invoice.project_title}</strong>.</p>
        <p>Amount Due: <strong>${float(invoice.amount):.2f}</strong></p>
        <p>Due Date: <strong>{invoice.due_date.strftime('%Y-%m-%d')}</strong></p>
        <p>
            <a href="{invoice_link}" 
               style="background:#17545B;color:#fff;padding:12px 18px;text-decoration:none;border-radius:6px;">
               View Invoice
            </a>
        </p>
        <p style="font-size:12px; color:#777;">Please make payment before the due date.</p>
    </div>
    """
    return send_email(client.email, f"Invoice for {invoice.project_title}", html)


def send_payment_received_email(client, amount, project):
    """Notify client and admin when payment is made."""
    project_link = f"{BASE_URL}/projects/{project.id}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">Payment Received</h3>
        <p>Hi <strong>{client.first_name}</strong>,</p>
        <p>We’ve received your payment of <strong>${float(amount):.2f}</strong> for <strong>{project.title}</strong>.</p>
        <p>Your funds are now held securely in escrow until project completion.</p>
        <p>
            <a href="{project_link}" style="color:#17545B; font-weight:600;">View Project →</a>
        </p>
    </div>
    """
    send_email(client.email, f"Payment Received - {project.title}", html)

    # Also notify admin
    admin_email = os.getenv("ADMIN_EMAIL", FROM_EMAIL)
    send_email(admin_email, f"Client Payment Received - {project.title}", html)
    return True


def send_funds_released_email(freelancer, client, project, amount):
    """Notify freelancer and client when funds are released."""
    project_link = f"{BASE_URL}/projects/{project.id}"
    html_freelancer = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">Funds Released!</h3>
        <p>Hi <strong>{freelancer.first_name}</strong>,</p>
        <p>Your payment of <strong>${float(amount):.2f}</strong> for <strong>{project.title}</strong> has been released to your wallet.</p>
        <p><a href="{project_link}" style="color:#17545B; font-weight:600;">View Project →</a></p>
    </div>
    """
    html_client = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#17545B;">Project Completed & Funds Released</h3>
        <p>Hi <strong>{client.first_name}</strong>,</p>
        <p>Your payment for <strong>{project.title}</strong> has been released to the freelancer.</p>
        <p><a href="{project_link}" style="color:#17545B; font-weight:600;">View Project →</a></p>
    </div>
    """
    send_email(freelancer.email, f"Funds Released - {project.title}", html_freelancer)
    send_email(client.email, f"Payment Released - {project.title}", html_client)
    return True


def send_refund_email(client, amount, project):
    """Notify client when refund is processed."""
    project_link = f"{BASE_URL}/projects/{project.id}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#e67e22;">Refund Processed</h3>
        <p>Hi <strong>{client.first_name}</strong>,</p>
        <p>Your refund of <strong>${float(amount):.2f}</strong> for <strong>{project.title}</strong> has been processed successfully.</p>
        <p>Funds have been returned to your wallet.</p>
        <p><a href="{project_link}" style="color:#17545B; font-weight:600;">View Project →</a></p>
    </div>
    """
    return send_email(client.email, f"Refund Processed - {project.title}", html)
