import logging
from typing import Dict, Any
from .base import BasePushProvider

logger = logging.getLogger(__name__)

class MockPushProvider(BasePushProvider):
    """
    Mock Push notification provider (Firebase FCM / Apple APNs abstraction).
    """

    def send(self, *, notification, **kwargs) -> Dict[str, Any]:
        logger.info(f"[PUSH MOCK] Recipient: {notification.recipient.email} | Title: {notification.title} | Body: {notification.message}")
        return {
            "success": True,
            "channel": "PUSH",
            "provider": "MockPushProvider",
            "message_id": f"push-mock-{notification.id}"
        }
