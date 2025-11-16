import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        from_email: Sender email address (defaults to SMTP_FROM_EMAIL env var)
    
    Returns:
        True if email was sent successfully, False otherwise
    
    Raises:
        Exception: If email sending fails
    """
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "newsletter@example.com")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    smtp_use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    
    # For development/testing, use console output if SMTP_HOST is not set properly
    if smtp_host == "localhost" and smtp_port == 1025:
        logger.info(f"[DEV MODE] Would send email to {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body[:100]}...")
        return True
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from_email
        msg["To"] = to_email
        
        text_part = MIMEText(body, "plain")
        msg.attach(text_part)
        
        if smtp_use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
        
        if smtp_use_tls and not smtp_use_ssl:
            server.starttls()
        
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
        raise

