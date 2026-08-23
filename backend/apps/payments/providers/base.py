from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePaymentProvider(ABC):
    """
    Abstract interface for payment gateway providers (e.g. Mock, TeleBirr, CBE Birr).
    """

    @abstractmethod
    def initiate_payment(self, *, payment, **kwargs) -> Dict[str, Any]:
        """
        Initiates a payment request with external provider.
        """
        pass

    @abstractmethod
    def verify_payment(self, *, payment, provider_transaction_id: str, **kwargs) -> Dict[str, Any]:
        """
        Verifies status of a payment with external provider.
        """
        pass

    @abstractmethod
    def handle_webhook(self, *, payload: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses and validates incoming webhook payloads.
        """
        pass

    @abstractmethod
    def initiate_payout(self, *, payout, **kwargs) -> Dict[str, Any]:
        """
        Initiates a transporter payout with external provider.
        """
        pass
