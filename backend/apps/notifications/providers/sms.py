import logging
from typing import Dict, Any
from .base import BaseSMSProvider

logger = logging.getLogger(__name__)

class MockSMSProvider(BaseSMSProvider):
    """
    Mock SMS provider for development and testing.
    Logs SMS delivery without invoking external Ethiopian telecom SMS API.
    """

    def send(self, *, notification, **kwargs) -> Dict[str, Any]:
        phone = getattr(notification.recipient, 'phone_number', '+251900000000') or '+251900000000'
        logger.info(f"[SMS MOCK] To: {phone} ({notification.recipient.email}) | Body: {notification.message}")
        return {
            "success": True,
            "channel": "SMS",
            "provider": "MockSMSProvider",
            "phone": phone,
            "message_id": f"sms-mock-{notification.id}"
        }
