"""Binary sensor platform for SunPi."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .coordinator import SunPiDataUpdateCoordinator
from .entity import SunPiEntity, SunPiSensorEntityDescription

BINARY_SENSORS = [
    SunPiSensorEntityDescription(
        name="Currently disinfecting",
        key="disinfecting",
        icon="mdi:bacteria-outline",
    ),
    SunPiSensorEntityDescription(
        name="Gas boiler status",
        key="relayStatus",
        icon="mdi:water-boiler",
    ),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator: SunPiDataUpdateCoordinator = config_entry.runtime_data.coordinator

    async_add_devices(
        SunPiBinarySensor(
            coordinator=coordinator,
            sensor_key=entity_description.key,
            entity_description=entity_description,
        )
        for entity_description in BINARY_SENSORS
    )


class SunPiBinarySensor(SunPiEntity, BinarySensorEntity):
    """SunPi binary_sensor class."""

    def __init__(
        self,
        sensor_key: str,
        coordinator: SunPiDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, sensor_key)
        self.entity_description = entity_description


    @property
    def entity_registry_enabled_default(self):
        """Return whether the sensor should be enabled by default."""
        return self.entity_description.entity_registry_enabled_default

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.getValue(self.entity_description.key))