"""Sensor platform for DBS SMS integration."""
from __future__ import annotations
from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_components.dbs_sms.const import DOMAIN
from custom_components.dbs_sms.exceptions import DBSBaseSMSError
from custom_components.dbs_sms.providers import BaseSMSProvider

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the DBS SMS sensor platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    provider: BaseSMSProvider = entry_data["provider"]

    async def async_update_data() -> dict:
        """Fetch data from the SMS provider API."""
        try:
            return await provider.async_get_info()
        except DBSBaseSMSError as err:
            raise UpdateFailed(f"Błąd komunikacji z API dostawcy: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Nieoczekiwany błąd pobierania danych: {err}") from err

    # Set up DataUpdateCoordinator to share updates between sensors
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"dbs_sms_coordinator_{entry.entry_id}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=30),
    )

    # Store coordinator reference back in hass.data
    entry_data["coordinator"] = coordinator

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    entities = [
        DBSSMSBalanceSensor(coordinator, entry),
        DBSSMSExpirySensor(coordinator, entry),
    ]

    async_add_entities(entities)

class DBSSMSBalanceSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Sensor showing the remaining SMS balance."""

    _attr_icon = "mdi:sms"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: DataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        
        # Unique ID based on integration config entry ID
        self._attr_unique_id = f"{entry.entry_id}_balance"
        self._attr_name = f"DBS SMS Balance ({entry.title})"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("balance")

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        return "SMS"

class DBSSMSExpirySensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Sensor showing the account expiration date."""

    _attr_icon = "mdi:calendar-clock"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self, coordinator: DataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_valid_to"
        self._attr_name = f"DBS SMS Account Expiry ({entry.title})"

    @property
    def native_value(self) -> datetime | None:
        """Return the expiration date converted to UTC datetime."""
        if self.coordinator.data is None:
            return None
        
        valid_to_str = self.coordinator.data.get("valid_to")
        if not valid_to_str:
            return None

        try:
            # HostedSMS date is in Europe/Warsaw timezone. We parse it:
            # Format usually: 2025-12-20T12:22:05
            dt = datetime.fromisoformat(valid_to_str)
            if dt.tzinfo is None:
                # Localize naive datetime to Europe/Warsaw
                warsaw_tz = ZoneInfo("Europe/Warsaw")
                dt = dt.replace(tzinfo=warsaw_tz)
            # Home Assistant expects a timezone-aware datetime in UTC
            return dt.astimezone(ZoneInfo("UTC"))
        except Exception as err:
            _LOGGER.warning("Nie udało się sparsować daty ważności konta '%s': %s", valid_to_str, err)
            return None
