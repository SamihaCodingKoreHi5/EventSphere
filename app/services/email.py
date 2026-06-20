import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import requests
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmailService")


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> bool:
        """
        Sends an email based on the configured EMAIL_BACKEND.
        Options: console, smtp, resend
        """
        backend = settings.EMAIL_BACKEND.lower()
        
        if backend == "console":
            return EmailService._send_to_console(to_email, subject, body)
        elif backend == "smtp":
            return EmailService._send_via_smtp(to_email, subject, body)
        elif backend == "resend":
            return EmailService._send_via_resend(to_email, subject, body)
        else:
            logger.warning(f"Unknown email backend '{backend}'. Defaulting to console.")
            return EmailService._send_to_console(to_email, subject, body)

    @staticmethod
    def _send_to_console(to_email: str, subject: str, body: str) -> bool:
        """Logs the email details to the server console (perfect for development/testing)."""
        logger.info("\n" + "="*50 + f"\n[EMAIL SENT]\nTo: {to_email}\nSubject: {subject}\nBody:\n{body}\n" + "="*50)
        return True

    @staticmethod
    def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
        """Sends an email using standard SMTP settings."""
        if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.error("SMTP configurations are missing. Falling back to console.")
            return EmailService._send_to_console(to_email, subject, body)
        
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            # Connect using TLS
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
            server.quit()
            logger.info(f"SMTP email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
            return False

    @staticmethod
    def _send_via_resend(to_email: str, subject: str, body: str) -> bool:
        """Sends an email using Resend HTTP API."""
        if not settings.RESEND_API_KEY:
            logger.error("Resend API key is missing. Falling back to console.")
            return EmailService._send_to_console(to_email, subject, body)

        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "from": settings.EMAIL_FROM,
                "to": to_email,
                "subject": subject,
                "html": body
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logger.info(f"Resend email successfully sent to {to_email}")
                return True
            else:
                logger.error(f"Resend API error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
            return False


def send_rsvp_confirmation(to_email: str, user_name: str, event_title: str, event_date: str, event_location: str):
    """Triggers RSVP confirmation email."""
    subject = f"RSVP Confirmed: {event_title}"
    body = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>Your RSVP for <strong>{event_title}</strong> has been successfully confirmed!</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li><strong>Date/Time:</strong> {event_date}</li>
                <li><strong>Location:</strong> {event_location}</li>
            </ul>
            <br>
            <p>We look forward to seeing you there!</p>
            <p>Best regards,<br>The EventSphere Team</p>
        </body>
    </html>
    """
    return EmailService.send_email(to_email, subject, body)


def send_event_reminder(to_email: str, user_name: str, event_title: str, event_date: str, event_location: str):
    """Triggers event reminder email."""
    subject = f"Reminder: {event_title} is coming up!"
    body = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>This is a friendly reminder that the event <strong>{event_title}</strong> you RSVP'd for is coming up soon.</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li><strong>Date/Time:</strong> {event_date}</li>
                <li><strong>Location:</strong> {event_location}</li>
            </ul>
            <br>
            <p>Don't forget to mark your calendar!</p>
            <p>Best regards,<br>The EventSphere Team</p>
        </body>
    </html>
    """
    return EmailService.send_email(to_email, subject, body)
