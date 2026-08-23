from .base import BaseNotificationProvider, BaseEmailProvider, BaseSMSProvider, BasePushProvider
from .email import MockEmailProvider
from .sms import MockSMSProvider
from .push import MockPushProvider

def get_notification_provider(channel: str) -> BaseNotificationProvider:
    """
    Factory function returning channel-specific provider instance.
    """
    if channel == 'EMAIL':
        return MockEmailProvider()
    elif channel == 'SMS':
        return MockSMSProvider()
    elif channel == 'PUSH':
        return MockPushProvider()
    # Default for IN_APP or unknown: MockPushProvider
    return MockPushProvider()

__all__ = [
    'BaseNotificationProvider',
    'BaseEmailProvider',
    'BaseSMSProvider',
    'BasePushProvider',
    'MockEmailProvider',
    'MockSMSProvider',
    'MockPushProvider',
    'get_notification_provider',
]
