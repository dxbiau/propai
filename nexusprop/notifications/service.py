"""
Notification service — WhatsApp, SMS, and Email delivery.

Sends Golden Opportunity alerts and deal notifications to users
via their preferred channel using Twilio and SendGrid.
"""

from __future__ import annotations

from typing import Optional

import structlog

from nexusprop.config.settings import get_settings
from nexusprop.models.user import NotificationChannel

logger = structlog.get_logger(__name__)


class NotificationService:
    """
    Multi-channel notification delivery service.

    Supports WhatsApp, SMS, and Email.
    Uses Twilio for WhatsApp/SMS and SendGrid for Email.
    """

    def __init__(self):
        self.settings = get_settings()
        self._twilio_client = None

    def _get_twilio(self):
        """Lazy-init Twilio client."""
        if self._twilio_client is None:
            try:
                from twilio.rest import Client
                self._twilio_client = Client(
                    self.settings.twilio_account_sid,
                    self.settings.twilio_auth_token,
                )
            except Exception as e:
                logger.warning("twilio_init_failed", error=str(e))
        return self._twilio_client

    async def send(
        self,
        channel: NotificationChannel,
        message: str,
        to: str,
        subject: Optional[str] = None,
    ) -> bool:
        """
        Send a notification via the specified channel.

        Args:
            channel: WhatsApp, SMS, Email, or Push
            message: The notification message
            to: Phone number or email address
            subject: Email subject (email only)
        """
        try:
            if channel == NotificationChannel.WHATSAPP:
                return await self._send_whatsapp(message, to)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(message, to)
            elif channel == NotificationChannel.EMAIL:
                return await self._send_email(message, to, subject)
            elif channel == NotificationChannel.PUSH:
                logger.info("push_notification_placeholder", to=to)
                return True
            else:
                logger.warning("unknown_channel", channel=channel)
                return False
        except Exception as e:
            logger.error("notification_send_failed", channel=channel, to=to, error=str(e))
            return False

    async def _send_whatsapp(self, message: str, to: str) -> bool:
        """Send a WhatsApp message via Twilio."""
        client = self._get_twilio()
        if not client:
            logger.warning("twilio_not_configured_whatsapp")
            return False

        # Ensure WhatsApp format
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"

        msg = client.messages.create(
            body=message,
            from_=self.settings.twilio_whatsapp_from,
            to=to,
        )

        logger.info("whatsapp_sent", sid=msg.sid, to=to)
        return True

    async def _send_sms(self, message: str, to: str) -> bool:
        """Send an SMS via Twilio."""
        client = self._get_twilio()
        if not client:
            logger.warning("twilio_not_configured_sms")
            return False

        # Truncate for SMS (160 chars standard, but Twilio handles concatenation)
        if len(message) > 1600:
            message = message[:1597] + "..."

        msg = client.messages.create(
            body=message,
            from_=self.settings.twilio_sms_from,
            to=to,
        )

        logger.info("sms_sent", sid=msg.sid, to=to)
        return True

    async def _send_email(
        self,
        message: str,
        to: str,
        subject: Optional[str] = None,
    ) -> bool:
        """Send an email via SendGrid."""
        if not self.settings.sendgrid_api_key:
            logger.warning("sendgrid_not_configured")
            return False

        import httpx

        subject = subject or "🏡 Australian Property Associates — New Investment Signal"

        # SendGrid v3 API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {self.settings.sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [{"to": [{"email": to}]}],
                    "from": {"email": self.settings.from_email, "name": "Australian Property Associates"},
                    "subject": subject,
                    "content": [
                        {"type": "text/plain", "value": message},
                        {"type": "text/html", "value": self._format_html_email(message)},
                    ],
                },
            )

            if response.status_code in (200, 201, 202):
                logger.info("email_sent", to=to)
                return True
            else:
                logger.warning("email_send_failed", status=response.status_code, body=response.text)
                return False

    def _format_html_email(self, message: str) -> str:
        """Wrap a plain text message in a branded HTML email template."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07); }}
        .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); padding: 24px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 24px; }}
        .header p {{ color: #93c5fd; margin: 8px 0 0 0; font-size: 14px; }}
        .content {{ padding: 24px; line-height: 1.6; color: #1e293b; white-space: pre-wrap; }}
        .footer {{ padding: 16px 24px; background: #f1f5f9; text-align: center; font-size: 12px; color: #64748b; }}
        .cta {{ display: inline-block; background: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Australian Property Associates</h1>
            <p>Your Digital Property Associate</p>
        </div>
        <div class="content">
            {message}
            <br><br>
            <a href="#" class="cta">View Full Analysis →</a>
        </div>
        <div class="footer">
            Australian Property Associates Pty Ltd | Investment-Grade Real Estate Intelligence<br>
            <a href="#">Manage Preferences</a> | <a href="#">Unsubscribe</a>
        </div>
    </div>
</body>
</html>
"""

    async def send_batch(
        self,
        notifications: list[dict],
    ) -> dict:
        """
        Send a batch of notifications.

        Each dict should have: channel, message, to, (optional) subject
        """
        sent = 0
        failed = 0

        for notif in notifications:
            channel = NotificationChannel(notif.get("channel", "email"))
            to = notif.get("phone") or notif.get("email", "")
            message = notif.get("message", "")
            subject = notif.get("subject")

            if not to or not message:
                failed += 1
                continue

            success = await self.send(channel, message, to, subject)
            if success:
                sent += 1
            else:
                failed += 1

        logger.info("batch_notifications_sent", sent=sent, failed=failed)
        return {"sent": sent, "failed": failed}
