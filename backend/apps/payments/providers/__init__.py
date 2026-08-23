from .base import BasePaymentProvider
from .mock import MockPaymentProvider

def get_payment_provider(provider_name: str = 'MOCK') -> BasePaymentProvider:
    """
    Factory function returning the configured PaymentProvider instance.
    """
    if provider_name in ['MOCK', 'TELEBIRR', 'CBE_BIRR']:
        return MockPaymentProvider()
    return MockPaymentProvider()

__all__ = [
    'BasePaymentProvider',
    'MockPaymentProvider',
    'get_payment_provider',
]
