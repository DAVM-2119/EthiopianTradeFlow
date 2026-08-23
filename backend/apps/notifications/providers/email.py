import logging
from typing import Dict, Any
from .base import BaseEmailProvider

logger = logging.getLogger(__name__)

class MockEmailProvider(BaseEmailProvider):
    """
    Mock Email provider for development and testing.
    Logs email delivery details without invoking external SMTP.
    """

    def send(self, *, notification, **kwargs) -> Dict[str, Any]:
        logger.info(f"[EMAIL MOCK] To: {notification.recipient.email} | Subject: {notification.title} | Body: {notification.message}")
        return {
            "success": True,
            "channel": "EMAIL",
            "provider": "MockEmailProvider",
            "recipient": notification.recipient.email,
            "message_id": f"email-mock-{notification.id}"
        }
