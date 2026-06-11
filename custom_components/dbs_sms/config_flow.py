"""Config flow for DBS SMS integration."""
from __future__ import annotations
from typing import Any
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from custom_components.dbs_sms.const import (
    CONF_COST_CENTER,
    CONF_DEFAULT_SENDER,
    CONF_PROVIDER,
    DOMAIN,
    PROVIDER_HOSTEDSMS,
    PROVIDERS,
)
from custom_components.dbs_sms.exceptions import (
    InvalidAuthError,
    SMSConnectionError,
    SMSProviderError,
)
from custom_components.dbs_sms.providers import get_provider

_LOGGER = logging.getLogger(__name__)

class DBSSMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DBS SMS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._provider_type: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: User selects the SMS provider."""
        if user_input is not None:
            self._provider_type = user_input[CONF_PROVIDER]
            # Route to the appropriate provider configuration step
            if self._provider_type == PROVIDER_HOSTEDSMS:
                return await self.async_step_hostedsms()

        # Step 1 Schema: Select provider dropdown
        data_schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=k, label=v)
                            for k, v in PROVIDERS.items()
                        ],
                        mode="dropdown",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema
        )

    async def async_step_hostedsms(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2 (HostedSMS.pl): User enters credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            default_sender = user_input[CONF_DEFAULT_SENDER]
            cost_center = user_input.get(CONF_COST_CENTER)

            try:
                # Verify credentials and cost center with the API
                provider = get_provider(
                    self.hass, PROVIDER_HOSTEDSMS, username, password, default_sender, cost_center
                )
                await provider.async_get_info()
            except InvalidAuthError:
                errors["base"] = "invalid_auth"
            except SMSConnectionError:
                errors["base"] = "cannot_connect"
            except SMSProviderError as err:
                _LOGGER.error("Błąd dostawcy HostedSMS podczas konfiguracji: %s", err)
                errors["base"] = "provider_error"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Nieoczekiwany błąd podczas konfiguracji: %s", err)
                errors["base"] = "unknown"
            else:
                # Successfully authenticated, save config entry
                return self.async_create_entry(
                    title=f"DBS SMS (HostedSMS.pl - {username})",
                    data={
                        CONF_PROVIDER: PROVIDER_HOSTEDSMS,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_DEFAULT_SENDER: default_sender,
                        CONF_COST_CENTER: cost_center,
                    },
                )

        # Step 2 Schema for HostedSMS.pl
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=user_input.get(CONF_USERNAME) if user_input else vol.UNDEFINED,
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.EMAIL
                    )
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=user_input.get(CONF_PASSWORD) if user_input else vol.UNDEFINED,
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
                vol.Required(
                    CONF_DEFAULT_SENDER,
                    default=user_input.get(CONF_DEFAULT_SENDER) if user_input else "INFO",
                ): selector.TextSelector(),
                vol.Optional(
                    CONF_COST_CENTER,
                    default=user_input.get(CONF_COST_CENTER) if user_input else vol.UNDEFINED,
                ): selector.TextSelector(),
            }
        )

        return self.async_show_form(
            step_id="hostedsms", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DBSSMSOptionsFlowHandler:
        """Create the options flow."""
        return DBSSMSOptionsFlowHandler(config_entry)


class DBSSMSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for DBS SMS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            default_sender = user_input[CONF_DEFAULT_SENDER]
            cost_center = user_input.get(CONF_COST_CENTER)
            provider_type = self.config_entry.data[CONF_PROVIDER]

            try:
                # Verify credentials with new parameters
                provider = get_provider(
                    self.hass, provider_type, username, password, default_sender, cost_center
                )
                await provider.async_get_info()
            except InvalidAuthError:
                errors["base"] = "invalid_auth"
            except SMSConnectionError:
                errors["base"] = "cannot_connect"
            except SMSProviderError as err:
                _LOGGER.error("Błąd dostawcy podczas edycji opcji: %s", err)
                errors["base"] = "provider_error"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Nieoczekiwany błąd podczas edycji opcji: %s", err)
                errors["base"] = "unknown"
            else:
                # Update config entry data directly
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_DEFAULT_SENDER: default_sender,
                        CONF_COST_CENTER: cost_center,
                    },
                )
                return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self.config_entry.data[CONF_USERNAME],
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.EMAIL
                    )
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=self.config_entry.data[CONF_PASSWORD],
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
                vol.Required(
                    CONF_DEFAULT_SENDER,
                    default=self.config_entry.data.get(CONF_DEFAULT_SENDER, "INFO"),
                ): selector.TextSelector(),
                vol.Optional(
                    CONF_COST_CENTER,
                    default=self.config_entry.data.get(CONF_COST_CENTER, vol.UNDEFINED),
                ): selector.TextSelector(),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
