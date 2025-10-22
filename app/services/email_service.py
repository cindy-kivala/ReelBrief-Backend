"""
Email Service
Owner: Caleb
Description: Handles all email notifications and templating for system messages.
"""
import os

from extensions import sg
from sendgrid.helpers.mail import Mail

FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@reelbrief.com")

def send_email(recipient, subject, html_content):
    """
    Generic email sender using SendGrid.
    """
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipient,  
        subject=subject,
        html_content=html_content
    )

    try:
        response = sg.send(message)
        print(f"Email sent to {recipient}, status: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return False


def send_password_reset_email(user):
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
    <p>Hello {freelancer.name},</p>
    <p>You've been assigned to a new project: <b>{project.title}</b>.</p>
    <p>Please log in to your dashboard to view more details.</p>
    """
    return send_email(freelancer.email, "New Project Assignment", html_content)


def send_payment_notification(transaction):
    """
    Notifies a freelancer or client about payment updates.
    """
    recipient = transaction.user.email
    html_content = f"""
    <h3>Payment Notification</h3>
    <p>Hello {transaction.user.name},</p>
    <p>Your payment of <b>${transaction.amount}</b> has been successfully processed.</p>
    <p>Transaction ID: {transaction.id}</p>
    """
    return send_email(recipient, "Payment Notification", html_content)
