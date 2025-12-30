"""Email service using Resend for transactional emails."""

import resend
from typing import Optional
import os

# Initialize Resend with API key from environment
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Default sender email (must be verified in Resend dashboard)
DEFAULT_FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@codemurf.com")
DEFAULT_FROM_NAME = os.getenv("FROM_NAME", "Codemurf")


def get_password_reset_html(reset_url: str, user_name: Optional[str] = None) -> str:
    """Generate HTML email template for password reset."""
    name = user_name or "there"
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #040406;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 500px; width: 100%; border-collapse: collapse;">
                    <!-- Logo -->
                    <tr>
                        <td align="center" style="padding-bottom: 30px;">
                            <h1 style="color: #ffffff; font-size: 24px; margin: 0;">Codemurf</h1>
                        </td>
                    </tr>
                    
                    <!-- Card -->
                    <tr>
                        <td style="background: rgba(13, 17, 23, 0.95); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 40px;">
                            <h2 style="color: #ffffff; font-size: 20px; margin: 0 0 16px 0; text-align: center;">Reset Your Password</h2>
                            <p style="color: #9ca3af; font-size: 14px; line-height: 1.6; margin: 0 0 24px 0; text-align: center;">
                                Hi {name}, we received a request to reset your password. Click the button below to set a new password.
                            </p>
                            
                            <!-- Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{reset_url}" style="display: inline-block; background: #ffffff; color: #000000; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 14px;">
                                            Reset Password
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="color: #6b7280; font-size: 12px; line-height: 1.5; margin: 24px 0 0 0; text-align: center;">
                                This link will expire in 15 minutes. If you didn't request this, you can safely ignore this email.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding-top: 30px; text-align: center;">
                            <p style="color: #6b7280; font-size: 12px; margin: 0;">
                                © 2024 Codemurf. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


async def send_password_reset_email(
    to_email: str,
    reset_url: str,
    user_name: Optional[str] = None
) -> dict:
    """
    Send password reset email using Resend.
    
    Args:
        to_email: Recipient email address
        reset_url: Password reset URL with token
        user_name: Optional user name for personalization
    
    Returns:
        dict with 'success' and 'message' or 'error'
    """
    if not resend.api_key:
        print("[email_service] RESEND_API_KEY not configured, skipping email")
        return {"success": False, "error": "Email service not configured"}
    
    try:
        html_content = get_password_reset_html(reset_url, user_name)
        
        params = {
            "from": f"{DEFAULT_FROM_NAME} <{DEFAULT_FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Reset Your Password - Codemurf",
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        
        print(f"[email_service] Password reset email sent to {to_email}, id: {email.get('id')}")
        return {"success": True, "message": "Email sent", "id": email.get("id")}
        
    except Exception as e:
        print(f"[email_service] Error sending email: {e}")
        return {"success": False, "error": str(e)}


async def send_welcome_email(
    to_email: str,
    user_name: Optional[str] = None
) -> dict:
    """
    Send welcome email to new users.
    
    Args:
        to_email: Recipient email address
        user_name: Optional user name for personalization
    """
    if not resend.api_key:
        return {"success": False, "error": "Email service not configured"}
    
    name = user_name or "there"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to Codemurf</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #040406;">
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table style="max-width: 500px; width: 100%; background: rgba(13, 17, 23, 0.95); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 40px;">
                    <tr>
                        <td>
                            <h1 style="color: #ffffff; font-size: 24px; margin: 0 0 20px 0;">Welcome to Codemurf! 🚀</h1>
                            <p style="color: #9ca3af; font-size: 14px; line-height: 1.6;">
                                Hi {name}, thanks for joining Codemurf! You now have access to our AI-powered VS Code extension that helps you write code 10x faster.
                            </p>
                            <p style="color: #9ca3af; font-size: 14px; line-height: 1.6; margin-top: 20px;">
                                Get started by installing the extension from the VS Code Marketplace.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    try:
        params = {
            "from": f"{DEFAULT_FROM_NAME} <{DEFAULT_FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Welcome to Codemurf! 🚀",
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
        
    except Exception as e:
        print(f"[email_service] Error sending welcome email: {e}")
        return {"success": False, "error": str(e)}
