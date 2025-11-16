import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> bool:
    """
    Send an email using Brevo (formerly Sendinblue) API.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        from_email: Sender email address (defaults to BREVO_FROM_EMAIL env var)
        from_name: Sender name (defaults to BREVO_FROM_NAME env var)

    Returns:
        True if email was sent successfully, False otherwise

    Raises:
        Exception: If email sending fails
    """
    brevo_api_key = os.getenv("BREVO_API_KEY")
    brevo_from_email = from_email or os.getenv(
        "BREVO_FROM_EMAIL", "newsletter@example.com"
    )
    brevo_from_name = from_name or os.getenv("BREVO_FROM_NAME", "Newsletter Service")

    if not brevo_api_key:
        logger.warning(
            "[DEV MODE] BREVO_API_KEY not set, logging email instead of sending"
        )
        logger.info("Would send email to %s", to_email)
        logger.info("From: %s <%s>", brevo_from_name, brevo_from_email)
        logger.info("Subject: %s", subject)
        logger.info("Body: %s...", body[:100])
        return True

    brevo_api_url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {"name": brevo_from_name, "email": brevo_from_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": body,
        "textContent": body,
    }

    try:
        response = requests.post(
            brevo_api_url, json=payload, headers=headers, timeout=10
        )
        response.raise_for_status()

        logger.info("Email sent successfully to %s via Brevo", to_email)
        return True

    except requests.exceptions.HTTPError as e:
        error_msg = f"Brevo API error: {e.response.status_code} - {e.response.text}"
        logger.error(
            "Failed to send email to %s: %s", to_email, error_msg, exc_info=True
        )
        raise RuntimeError(error_msg) from e
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(
            "Failed to send email to %s: %s", to_email, error_msg, exc_info=True
        )
        raise RuntimeError(error_msg) from e
    except Exception as e:
        logger.error(
            "Unexpected error sending email to %s: %s", to_email, str(e), exc_info=True
        )
        raise
