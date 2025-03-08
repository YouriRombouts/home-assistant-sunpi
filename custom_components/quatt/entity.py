"""QuattEntity class."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SunPiDataUpdateCoordinator

class SunPiSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    """A class that describes Quatt sensor entities."""

class SunPiEntity(CoordinatorEntity):
    """SunPiEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SunPiDataUpdateCoordinator,
        sensor_key: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id + sensor_key

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "SunPi",
            "model": self.coordinator.getValue("system.hostName"),
        }
