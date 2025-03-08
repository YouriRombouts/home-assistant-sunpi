"""Adds config flow for Quatt."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers import selector

from .api import (
    SunPiApiClient,
    APIConnectionError,
    APITimeoutError,
)

from .const import (
    DOMAIN,
    LOGGER,
)


class SunPiFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for SunPi."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize a SunPi flow."""
        self.ip_address: str | None = None
        self.hostname: str | None = None

    async def _test_credentials(self, ip_address: str) -> str:
        """Validate credentials."""
        client = SunPiApiClient(ip_address)
        return await client.async_get_data()

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                data = await self._test_credentials(
                    ip_address=user_input[CONF_IP_ADDRESS],
                )
            except APIConnectionError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "unknown"
            except APITimeoutError as exception:
                LOGGER.error(exception)
                _errors["base"] = "timeout"
            else:
                if data is not None:
                    # Check if this cic has already been configured
                    await self.async_set_unique_id("SunPi")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="SunPi",
                        data=user_input,
                    )


        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=(user_input or {}).get(CONF_IP_ADDRESS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )