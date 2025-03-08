"""Custom integration to integrate SunPi with Home Assistant."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import SunPiApiClient
from .const import SCAN_INTERVAL
from .coordinator import SunPiDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

@dataclass
class RuntimeData:
    """Class to hold your data."""
    coordinator: SunPiDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[RuntimeData]) -> bool:
    """Set up this integration using UI."""
    coordinator = SunPiDataUpdateCoordinator(
        hass=hass,
        update_interval=config_entry.options.get(SCAN_INTERVAL),
        client=SunPiApiClient(config_entry.data[CONF_IP_ADDRESS]),
    )
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.client.connected:
        raise ConfigEntryNotReady

    config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    config_entry.runtime_data = RuntimeData(coordinator)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle config options update."""
    # Reload the integration when the options change.
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry[RuntimeData]) -> bool:
    """Unload a config entry."""
    # This is called when you remove your integration or shutdown HA.
    # If you have created any custom services, they need to be removed here too.

    # Unload platforms and return result
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def _get_data_for_test(hass: HomeAssistant, ip_address: str) -> bool:
    """Validate credentials."""
    client = SunPiApiClient(ip_address=ip_address)
    data = await client.async_get_data()
    return data is not None