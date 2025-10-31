# app/services/email_service.py
"""
Email Service
Owner: Ryan (final)
Centralized outbound email (verification, password reset, admin alerts, etc.)
"""

from typing import Tuple, Optional  # 3.8-safe typing
import logging
import os

from itsdangerous import URLSafeTimedSerializer
from sendgrid.helpers.mail import From, Mail

from app.extensions import sg  # Initialized SendGrid client (or None)

# ---- Config ----
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5174")
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

# ---- Low-level sender ----
def send_email(recipient: str, subject: str, html_content: str, from_name: Optional[str] = None) -> bool:
    if not sg:
        LOGGER.error("❌ SendGrid client not configured. Set SENDGRID_API_KEY.")
        return False

    message = Mail(
        from_email=From(FROM_EMAIL, from_name or FROM_NAME),
        to_emails=recipient,
        subject=subject,
        html_content=html_content,
    )

    try:
        response = sg.send(message)
        status = getattr(response, "status_code", None)
        LOGGER.info("📧 Email send attempt → %s | status=%s", recipient, status)
        if status in (200, 202):
            return True
        LOGGER.error("⚠️ SendGrid non-OK status=%s body=%s", status, getattr(response, "body", b""))
        return False
    except Exception as exc:
        LOGGER.exception("❌ SendGrid send failed: %s", exc)
        return False

# ---- Verification ----
def send_verification_email(email: str, user_id: int) -> Tuple[bool, str]:
    token = create_verification_token(user_id)
    verify_link = f"{BASE_URL}/verify-email/{token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color:#17545B; font-weight:600; margin-bottom:16px;">Welcome to ReelBrief 👋</h2>
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
    LOGGER.info("🔗 Verification link for %s: %s", email, verify_link)
    return ok, token

# ---- Password reset ----
def send_password_reset_email(user) -> bool:
    reset_token = getattr(user, "reset_token", None)
    if not reset_token:
        LOGGER.error("❌ send_password_reset_email called without reset_token on user id=%s", getattr(user, "id", None))
        return False

    reset_link = f"{BASE_URL}/reset-password/{reset_token}"
    name = _display_name(user)
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
    project_link = f"{BASE_URL}/projects/{getattr(project, 'id', '')}"
    name = _display_name(freelancer)
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h3 style="color:#27ae60;">New Project Assigned!</h3>
        <p>Hi <strong>{name}</strong>,</p>
        <p>You've been assigned to:</p>
        <h2 style="color:#2c3e50;">{getattr(project, 'title', 'A Project')}</h2>
        <p><a href="{project_link}" style="color:#3498db;">View Project →</a></p>
    </div>
    """
    return send_email(getattr(freelancer, "email", ""), f"New Project: {getattr(project, 'title', 'Project')}", html, from_name="ReelBrief Assignments")

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
    project_id = getattr(deliverable, "project_id", None)
    project_link = f"{BASE_URL}/projects/{project_id}" if project_id else BASE_URL
    deliverable_link = f"{BASE_URL}/deliverables/{getattr(deliverable, 'id', '')}"
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
    return send_email(getattr(freelancer, "email", ""), f"Deliverable Approved: {getattr(deliverable, 'title', 'Deliverable')}", html, from_name="ReelBrief Reviews")

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
    subject = f"Feedback: {getattr(deliverable, 'title', 'Deliverable')} – {'Revision Needed' if is_revision else 'Review'}"
    return send_email(getattr(recipient_user, "email", ""), subject, html, from_name="ReelBrief Feedback")

# ---- Admin alert: new freelancer CV ----
def send_admin_alert_new_freelancer_cv(user, file_name: str, file_url: Optional[str]) -> bool:
    # If no admin email configured, do nothing but succeed.
    if not ADMIN_ALERT_EMAIL:
        LOGGER.info("ℹ️ ADMIN_ALERT_EMAIL not set; skipping admin alert.")
        return True

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto;">
        <h3 style="color:#2c3e50;">New Freelancer Application</h3>
        <p><strong>Name:</strong> {_display_name(user)}</p>
        <p><strong>Email:</strong> {getattr(user, 'email', '')}</p>
        <p><strong>Uploaded CV:</strong> {file_name}</p>
        {"<p><a href='%s' style='color:#3498db;'>Open CV</a></p>" % file_url if file_url else ""}
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
        <p style="font-size:12px;color:#999;">You are receiving this because ADMIN_ALERT_EMAIL is configured.</p>
    </div>
    """
    return send_email(ADMIN_ALERT_EMAIL, "New Freelancer CV Submitted", html, from_name="ReelBrief Admin Alerts")

# ---- Back-compat alias (keeps older imports working) ----
def send_admin_freelancer_application_email(user, file_name: str, file_url: Optional[str]) -> bool:
    return send_admin_alert_new_freelancer_cv(user, file_name, file_url)

__all__ = [
    "create_verification_token",
    "send_email",
    "send_verification_email",
    "send_password_reset_email",
    "send_project_assignment_email",
    "send_payment_notification",
    "send_deliverable_approved_notification",
    "send_deliverable_feedback_notification",
    "send_admin_alert_new_freelancer_cv",
    "send_admin_freelancer_application_email",
]
