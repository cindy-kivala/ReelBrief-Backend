"""
Email Service
Owner: Ryan (final)
Description: Centralized SendGrid mailers (verification, reset, notifications).
"""

import os
import logging
from itsdangerous import URLSafeTimedSerializer
from sendgrid.helpers.mail import From, Mail
from app.extensions import sg

logger = logging.getLogger("email_service")

FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
FROM_NAME  = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
BASE_URL   = os.getenv("BASE_URL", "http://localhost:5174")
SECRET_KEY = os.getenv("SECRET_KEY", "devsecretkey")

def create_verification_token(user_id: int) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(user_id, salt="email-verify")

def send_email(recipient, subject, html_content, from_name: str = FROM_NAME) -> bool:
    if sg is None:
        logger.error("❌ SendGrid client not configured. Skipping send.")
        return False
    message = Mail(from_email=From(FROM_EMAIL, from_name), to_emails=recipient, subject=subject, html_content=html_content)
    try:
        resp = sg.send(message)
        ok = resp.status_code in (200, 202)
        if not ok:
            logger.error("SendGrid non-2xx: %s %s", resp.status_code, getattr(resp, "body", b"")[:200])
        return ok
    except Exception as e:
        logger.error("❌ SendGrid send failed: %s", e)
        return False

def send_verification_email(email: str, user_id: int):
    token = create_verification_token(user_id)
    link  = f"{BASE_URL}/verify-email/{token}"
    html  = f"""
    <div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;'>
      <h2 style='color:#17545B;'>Welcome to ReelBrief!</h2>
      <p>Hello <strong>{email}</strong>, please verify your email:</p>
      <p>
        <a href="{link}" style="background:#17545B;color:#fff;padding:12px 18px;border-radius:6px;text-decoration:none;">
          Verify Email
        </a>
      </p>
      <p style='color:#888'>Link expires in 1 hour.</p>
    </div>
    """
    ok = send_email(email, "Verify Your ReelBrief Email Address", html)
    return ok, token

def send_password_reset_email(user):
    link = f"{BASE_URL}/reset-password/{user.reset_token}"
    name = getattr(user, "first_name", None) or getattr(user, "name", "there")
    html = f"""
    <div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;'>
      <h3>Password Reset</h3>
      <p>Hi <strong>{name}</strong>, click below to reset your password:</p>
      <a href="{link}" style="background:#3498db;color:#fff;padding:12px 18px;border-radius:6px;text-decoration:none;">
        Reset Password
      </a>
    </div>
    """
    return send_email(user.email, "Reset Your ReelBrief Password", html)

# Extra names used elsewhere; keep them available
def send_project_assignment_email(project, freelancer):  # no-op-ish
    return True

def send_payment_notification(transaction):
    return True

def send_deliverable_approved_notification(deliverable, freelancer):
    return True

def send_deliverable_feedback_notification(deliverable, feedback, client):
    return True
