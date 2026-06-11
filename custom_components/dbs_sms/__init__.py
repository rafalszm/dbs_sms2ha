"""The DBS SMS integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.dbs_sms.const import (
    CONF_COST_CENTER,
    CONF_DEFAULT_SENDER,
    CONF_PROVIDER,
    DOMAIN,
)
from custom_components.dbs_sms.providers import get_provider

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DBS SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    provider_type = entry.data[CONF_PROVIDER]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    default_sender = entry.data.get(CONF_DEFAULT_SENDER)
    cost_center = entry.data.get(CONF_COST_CENTER)

    try:
        provider = get_provider(
            hass, provider_type, username, password, default_sender, cost_center
        )
        # Store provider and placeholder for coordinator
        hass.data[DOMAIN][entry.entry_id] = {
            "provider": provider,
            "coordinator": None,
        }
    except Exception as err:
        _LOGGER.error("Nie udało się utworzyć dostawcy SMS: %s", err)
        return False

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register send_sms service if not already registered
    if not hass.services.has_service(DOMAIN, "send_sms"):
        async def async_send_sms_service(call: ServiceCall) -> None:
            """Service to send SMS."""
            message = call.data["message"]
            targets = call.data["targets"]
            sender = call.data.get("sender")
            cost_center = call.data.get("cost_center")
            target_entry_id = call.data.get("config_entry")

            # Ensure targets is a list of strings (handles cases where UI passes integers/floats without quotes)
            if isinstance(targets, (int, float)):
                targets = [str(int(targets))]
            elif isinstance(targets, str):
                targets = [t.strip() for t in targets.split(",") if t.strip()]
            elif isinstance(targets, list):
                parsed_targets = []
                for t in targets:
                    if isinstance(t, (int, float)):
                        parsed_targets.append(str(int(t)))
                    elif t:
                        parsed_targets.append(str(t).strip())
                targets = parsed_targets
            else:
                # Fallback: try to convert whatever it is to a string representation
                try:
                    targets = [str(targets).strip()]
                except Exception:
                    raise HomeAssistantError("Format numerów odbiorców (targets) jest nieprawidłowy.")

            if not targets or not any(targets):
                raise HomeAssistantError("Lista odbiorców (targets) nie może być pusta.")

            # Find the provider
            active_entries = hass.data[DOMAIN]
            if not active_entries:
                raise HomeAssistantError("Brak skonfigurowanych kont DBS SMS.")

            selected_entry = None
            if target_entry_id:
                selected_entry = active_entries.get(target_entry_id)
                if not selected_entry:
                    raise HomeAssistantError(
                        f"Skonfigurowane konto o ID '{target_entry_id}' nie istnieje."
                    )
            else:
                # Use the first available config entry
                selected_entry = list(active_entries.values())[0]

            selected_provider = selected_entry["provider"]

            # Trigger async send
            try:
                await selected_provider.async_send_sms(targets, message, sender, cost_center=cost_center)
                
                # Refresh coordinator data in background to immediately reflect new balance
                coordinator = selected_entry.get("coordinator")
                if coordinator:
                    hass.async_create_task(coordinator.async_request_refresh())
            except Exception as err:
                raise HomeAssistantError(f"Błąd wysyłania SMS: {err}") from err

        hass.services.async_register(DOMAIN, "send_sms", async_send_sms_service)

    # Register update listener to handle options changes
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
        # If no config entries remain, remove the service
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "send_sms")
            hass.data.pop(DOMAIN, None)

    return unload_ok
