"""SunPi integration using DataUpdateCoordinator."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorDeviceClass
import homeassistant.util.dt as dt_util

from .api import SunPiApiClient, APIConnectionError, APITimeoutError
from .const import SCAN_INTERVAL, DOMAIN, LOGGER

class SunPiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: int,
        client: SunPiApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except APIConnectionError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except APITimeoutError as exception:
            raise UpdateFailed(exception) from exception

    def bottomTemperature(self):
        """Get temperature at the bottom of the vat."""
        LOGGER.debug(self.getValue("bottom"))
        return self.getValue("bottom")

    def middleTemperature(self):
        """Get temperature at the middle of the vat."""
        LOGGER.debug(self.getValue("middle"))
        return self.getValue("middle")

    def topTemperature(self):
        """Get temperature at the top of the vat."""
        LOGGER.debug(self.getValue("top"))
        return self.getValue("top")

    def getValue(self, key: str, default: float | None = None):
        if key is None: return default
        elif key not in self.data:
            LOGGER.warning("Could not find key: %s", key)
            return default

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP or self.entity_description.device_class == SensorDeviceClass.DATE:
            return dt_util.parse_datetime(self.data[key])
        elif self.entity_description.device_class == SensorDeviceClass.TEMPERATURE:
            return float(self.data[key])
        else:
            return bool(self.data[key])