"""
Email Service
Owner: Ryan
Description:
Safe development version — logs email actions instead of actually sending.
Replace with real Flask-Mail or SendGrid integration in production.
"""

import os

from sendgrid.helpers.mail import Mail

from app.extensions import sg

FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@reelbrief.com")


def send_email(recipient, subject, html_content):
    """
    Production-ready email with environment detection.
    """
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production and os.getenv('SENDGRID_API_KEY'):
        # PRODUCTION: Real emails
        message = Mail(
            from_email=FROM_EMAIL, 
            to_emails=recipient, 
            subject=subject, 
            html_content=html_content
        )
        try:
            response = sg.send(message)
            success = response.status_code in [200, 202]
            status = "sent" if success else f"failed ({response.status_code})"
            print(f"[PROD] Email {status} to {recipient}")
            return success
        except Exception as e:
            print(f"[PROD] Email failed to {recipient}: {e}")
            return False
    else:
        # DEVELOPMENT: Log only
        print(f"[DEV] Would send to: {recipient} | Subject: {subject}")
        return True  # Always succeed in development



def send_password_reset_email(user):  # CONFIRM WITH RYAN IF ITS CLAS OROBJ user or user.email
    """
    Sends a password reset link to the user.
    """
    reset_link = f"https://reelbrief.com/reset-password/{user.reset_token}"
    html_content = f"""
    <h3>Password Reset Request</h3>
    <p>Hello {user.name},</p>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}">Reset Password</a>
    <p>This link will expire in 30 minutes.</p>
    """
    return send_email(user.email, "Password Reset Instructions", html_content)


def send_project_assignment_email(project, freelancer):
    """
    Notifies a freelancer about a new project assignment.
    """
    html_content = f"""
    <h3>New Project Assignment</h3>
    <p>Hello {freelancer.first_name} {freelancer.last_name},</p>
    <p>You've been assigned to a new project: <b>{project.title}</b>.</p>
    <p>Please log in to your dashboard to view more details.</p>
    """
    return send_email(freelancer.email, "New Project Assignment", html_content)


def send_payment_notification(escrow_transaction, user):
    """
    Notifies a freelancer or client about payment updates.
    """
    # user = User.query.get(escrow_transaction.freelancer_id)
    # if not user:
    #     return False
    
    html_content = f"""
    <h3>Payment Notification</h3>
    <p>Hello {user.first_name} {user.last_name},</p>
    <p>Your payment of <b>${escrow_transaction.amount}</b> has been successfully processed.</p>
    <p>Transaction ID: {escrow_transaction.id}</p>
    <p>Invoice Number: {escrow_transaction.invoice_number}</p>
    """
    return send_email(user.email, "Payment Notification", html_content)

def send_verification_email(user_email, verification_token):
    """
    Sends email verification link to new user.
    """
    verification_link = f"https://reelbrief.com/verify-email/{verification_token}"
    html_content = f"""
    <h3>Email Verification</h3>
    <p>Hello,</p>
    <p>Thank you for registering with ReelBrief!</p>
    <p>Click the link below to verify your email address:</p>
    <a href="{verification_link}">Verify Email</a>
    <p>This link will expire in 24 hours.</p>
    """
    return send_email(user_email, "Verify Your Email - ReelBrief", html_content)


def send_deliverable_feedback_notification(user_email, deliverable_title, feedback_content):
    """
    Notifies freelancer of new feedback on their deliverable.
    """
    html_content = f"""
    <h3>New Feedback on Your Deliverable</h3>
    <p>Hello,</p>
    <p>You have received new feedback on: <b>{deliverable_title}</b></p>
    <p><i>"{feedback_content[:200]}..."</i></p>
    <p>Please log in to your dashboard to view full feedback and respond.</p>
    """
    return send_email(user_email, "New Feedback - ReelBrief", html_content)


def send_deliverable_approved_notification(user_email, deliverable_title, project_name):
    """
    Notifies freelancer that their deliverable was approved.
    """
    html_content = f"""
    <h3>Deliverable Approved!</h3>
    <p>Hello,</p>
    <p>Great news! Your deliverable <b>{deliverable_title}</b> for project <b>{project_name}</b> has been approved.</p>
    <p>Payment will be released shortly.</p>
    """
    return send_email(user_email, "Deliverable Approved - ReelBrief", html_content)


def send_payment_released_notification(user_email, amount, project_name):
    """
    Notifies freelancer that payment has been released.
    """
    html_content = f"""
    <h3>Payment Released!</h3>
    <p>Hello,</p>
    <p>Good news! Payment of <b>${amount}</b> for project <b>{project_name}</b> has been released to your account.</p>
    <p>Please allow 3-5 business days for the funds to appear in your account.</p>
    """
    return send_email(user_email, "Payment Released - ReelBrief", html_content)
