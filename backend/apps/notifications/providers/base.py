from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNotificationProvider(ABC):
    """
    Abstract base interface for notification delivery channel providers.
    """

    @abstractmethod
    def send(self, *, notification, **kwargs) -> Dict[str, Any]:
        """
        Delivers the notification payload via the channel.
        """
        pass


class BaseEmailProvider(BaseNotificationProvider):
    pass


class BaseSMSProvider(BaseNotificationProvider):
    pass


class BasePushProvider(BaseNotificationProvider):
    pass
