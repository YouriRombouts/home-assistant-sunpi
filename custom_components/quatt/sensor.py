"""Sensor platform for SunPi."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
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
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunPiSensorEntityDescription(
        name="Vat middle temperature",
        key="middle",
        icon="mdi:water-boiler",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunPiSensorEntityDescription(
        name="Vat top temperature",
        key="top",
        icon="mdi:water-boiler",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: SunPiDataUpdateCoordinator = config_entry.runtime_data.coordinator

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

        return value