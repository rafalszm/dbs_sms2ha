"""Custom exceptions for the DBS SMS integration."""
from homeassistant.exceptions import HomeAssistantError

class DBSBaseSMSError(HomeAssistantError):
    """Base exception for all DBS SMS errors."""

class SMSProviderError(DBSBaseSMSError):
    """General provider error."""

class InvalidAuthError(DBSBaseSMSError):
    """Authentication failed."""

class SMSConnectionError(DBSBaseSMSError):
    """Network connection or timeout error."""
