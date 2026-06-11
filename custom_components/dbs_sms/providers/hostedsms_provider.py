"""HostedSMS.pl provider implementation."""
import base64
import logging
import aiohttp
import uuid

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.dbs_sms.exceptions import (
    InvalidAuthError,
    SMSConnectionError,
    SMSProviderError,
)
from custom_components.dbs_sms.providers import BaseSMSProvider

_LOGGER = logging.getLogger(__name__)

class HostedSMSProvider(BaseSMSProvider):
    """Provider for HostedSMS.pl service."""

    async def _async_request(self, method: str, path: str, json_data: dict = None) -> dict:
        """Perform an HTTP request with automatic failover to the backup server."""
        session = async_get_clientsession(self.hass)
        
        # Prepare authorization header
        auth_str = f"{self.username}:{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
        }
        if json_data:
            headers["Content-Type"] = "application/json; charset=utf-8"

        # Primary and backup URLs
        urls = [
            f"https://api.hostedsms.pl/FullApi{path}",
            f"https://api2.hostedsms.pl/FullApi{path}",
        ]

        last_error = None
        for url in urls:
            try:
                _LOGGER.debug("Sending request: %s %s", method, url)
                async with session.request(
                    method, url, headers=headers, json=json_data, timeout=10
                ) as response:
                    if response.status == 401:
                        raise InvalidAuthError("Błąd autoryzacji w HostedSMS.pl (niepoprawny login lub hasło)")
                    
                    if response.status != 200:
                        text = await response.text()
                        _LOGGER.warning("Błąd API HostedSMS (%s): status=%s, body=%s", url, response.status, text)
                        raise SMSProviderError(f"API zwróciło kod statusu {response.status}")
                    
                    data = await response.json()
                    _LOGGER.debug("HostedSMS response from %s: %s", url, data)
                    
                    if isinstance(data, dict) and data.get("ErrorMessage"):
                        raise SMSProviderError(data["ErrorMessage"])
                    
                    return data
            except aiohttp.ClientConnectorError as err:
                _LOGGER.warning("Nie można połączyć się z %s: %s", url, err)
                last_error = err
            except aiohttp.ServerTimeoutError as err:
                _LOGGER.warning("Przekroczono limit czasu żądania dla %s: %s", url, err)
                last_error = err
            except Exception as err:
                if isinstance(err, (InvalidAuthError, SMSProviderError)):
                    raise
                _LOGGER.warning("Nieoczekiwany błąd podczas zapytania do %s: %s", url, err)
                last_error = err
        
        raise SMSConnectionError(f"Błąd połączenia z serwerami HostedSMS: {last_error}")

    async def async_send_sms(self, phones: list[str], message: str, sender: str = None, cost_center: str = None) -> bool:
        """Send an SMS via HostedSMS FullApi/Smses."""
        payload = {
            "Phone": phones,
            "Message": message,
            "Sender": sender or self.default_sender or "INFO",
            "TransactionId": uuid.uuid4().hex,
            "CostCenter": cost_center or self.cost_center or None,
        }
        await self._async_request("POST", "/Smses", json_data=payload)
        return True

    async def async_get_info(self) -> dict:
        """Get account details (remaining balance and expiration date)."""
        data = await self._async_request("GET", "/CustomerInfo")
        return {
            "balance": data.get("SmsCounter"),
            "valid_to": data.get("CustomerValidTo"),
        }
