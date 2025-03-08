"""Custom integration to integrate SunPi with Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .api import (
    SunPiApiClient,
    APIConnectionError,
    APITimeoutError,
)
from .const import SCAN_INTERVAL, DOMAIN, LOGGER
from .coordinator import SunPiDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = SunPiDataUpdateCoordinator(
        hass=hass,
        update_interval=entry.options.get(SCAN_INTERVAL),
        client=SunPiApiClient(entry.data[CONF_IP_ADDRESS]),
    )
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # On update of the options reload the entry which reloads the coordinator
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

async def _get_data_for_test(hass: HomeAssistant, ip_address: str) -> bool:
    """Validate credentials."""
    client = SunPiApiClient(ip_address=ip_address)
    data = await client.async_get_data()
    return data is not None

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""

    if config_entry.version == 1:
        # Migrate CONF_POWER_SENSOR from data to options
        # Set the unique_id of the cic
        LOGGER.debug("Migrating config entry from version '%s'", config_entry.version)

        # The old version does not have a unique_id so we get the CIC hostname and set it
        # Return that the migration failed in case the retrieval fails
        try:
            call_success = await _get_data_for_test(hass=hass, ip_address=config_entry.data[CONF_IP_ADDRESS])
            if not call_success: return False
        except APIConnectionError as exception:
            LOGGER.error(exception)
            return False
        except APITimeoutError as exception:
            LOGGER.error(exception)
            return False
        else:
            hostname_unique_id = "SunPi"

            new_data = {**config_entry.data}
            new_options = {**config_entry.options}

            # Update the config entry to version 2
            hass.config_entries.async_update_entry(
                config_entry,
                data=new_data,
                options=new_options,
                unique_id=hostname_unique_id,
                version=2
            )

    return True