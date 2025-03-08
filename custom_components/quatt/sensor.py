"""Sensor platform for quatt."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import EntityCategory
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import SunPiDataUpdateCoordinator
from .entity import SunPiSensorEntityDescription, SunPiEntity

SENSORS = [
    # Time
    SunPiSensorEntityDescription(
        name="Timestamp last update",
        key="time.tsHuman",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
    ),
    SunPiSensorEntityDescription(
        name="Vat bottom temperature",
        key="bottom",
        icon="mdi:water-boiler",
    ),
    SunPiSensorEntityDescription(
        name="Vat middle temperature",
        key="middle",
        icon="mdi:water-boiler",
    ),
    SunPiSensorEntityDescription(
        name="Vat top temperature",
        key="top",
        icon="mdi:water-boiler",
    ),
]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SunPiSensor(
            coordinator=coordinator,
            sensor_key=entity_description.key,
            entity_description=entity_description,
        )
        for entity_description in SENSORS
    )

class SunPiSensor(SunPiEntity, SensorEntity):
    """SunPi Sensor class."""

    def __init__(
        self,
        sensor_key: str,
        coordinator: SunPiDataUpdateCoordinator,
        entity_description: SunPiSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, sensor_key)
        self.entity_description = entity_description

    @property
    def entity_registry_enabled_default(self):
        """Return whether the sensor should be enabled by default."""
        value = self.entity_description.entity_registry_enabled_default
        return value

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        value = self.coordinator.getValue(self.entity_description.key)

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            value = dt_util.parse_datetime(value)

        return value