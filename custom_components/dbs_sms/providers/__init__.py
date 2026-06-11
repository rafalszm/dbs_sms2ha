"""Base class and interface for SMS providers."""
from abc import ABC, abstractmethod
import logging

_LOGGER = logging.getLogger(__name__)

class BaseSMSProvider(ABC):
    """Abstract base class for all SMS providers."""

    def __init__(self, hass, username: str, password: str, default_sender: str = None) -> None:
        """Initialize the provider."""
        self.hass = hass
        self.username = username
        self.password = password
        self.default_sender = default_sender

    @abstractmethod
    async def async_send_sms(self, phones: list[str], message: str, sender: str = None) -> bool:
        """Send an SMS to one or more phone numbers."""
        pass

    @abstractmethod
    async def async_get_info(self) -> dict:
        """Retrieve account details (balance, validity).

        Returns:
            dict: {
                "balance": float | int | None,
                "valid_to": str | None,
            }
        """
        pass


def get_provider(hass, provider_type: str, username: str, password: str, default_sender: str = None) -> BaseSMSProvider:
    """Get the appropriate provider implementation."""
    from custom_components.dbs_sms.const import PROVIDER_HOSTEDSMS
    from custom_components.dbs_sms.exceptions import SMSProviderError

    if provider_type == PROVIDER_HOSTEDSMS:
        from .hostedsms_provider import HostedSMSProvider
        return HostedSMSProvider(hass, username, password, default_sender)
    
    raise SMSProviderError(f"Nieobsługiwany dostawca SMS: {provider_type}")

