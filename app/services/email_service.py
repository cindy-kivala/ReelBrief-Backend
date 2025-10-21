# """
# Email Service
# Owner: Caleb
# Description: Handles all email notifications and templating for system messages.
# """

# # TODO: Caleb - Implement Email Service
# #
# # Required functions:
# #
# # def send_email(recipient, subject, template_name, context):
# #     """Send a templated email."""
# #
# # def send_password_reset_email(user):
# #     """Send password reset instructions."""
# #
# # def send_project_assignment_email(project, freelancer):
# #     """Notify freelancer of new project."""
# #
# # def send_payment_notification(transaction):
# #     """Notify freelancer or client about payment updates."""


"""
Email Service
Owner: Ryan
Description:
Safe development version — logs email actions instead of actually sending.
Replace with real Flask-Mail or SendGrid integration in production.
"""

import os
from flask import current_app


def send_verification_email(to_email, token):
    """
    Mock verification email sender.
    Prints the message instead of sending it.
    """
    base_url = current_app.config.get("FRONTEND_URLS", "http://localhost:5173").split(",")[0]
    verify_link = f"{base_url}/verify?token={token}"

    print("\n📧 [Mock Email] Verification Email")
    print(f"To: {to_email}")
    print(f"Subject: Verify your ReelBrief account")
    print(f"Verification link: {verify_link}\n")


def send_password_reset_email(to_email, token):
    """
    Mock password reset email sender.
    Prints the message instead of sending it.
    """
    base_url = current_app.config.get("FRONTEND_URLS", "http://localhost:5173").split(",")[0]
    reset_link = f"{base_url}/reset-password?token={token}"

    print("\n📧 [Mock Email] Password Reset Email")
    print(f"To: {to_email}")
    print(f"Subject: Reset your ReelBrief password")
    print(f"Reset link: {reset_link}\n")
