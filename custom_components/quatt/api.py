import asyncio
import logging
from aiohttp import ClientSession

from .const import LOGGER

_RETRY_ATTEMPTS = 3

class SunPiApiClient:
    """SunPi API Client."""

    def __init__(self, host: str, session: ClientSession) -> None:
        self.host = host
        self.session = session
        self.connected: bool = False

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(method="get", path="/status")

    async def _api_wrapper(
        self,
        method: str,
        path: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        url = "http://" + self.host + path

        for attempt in range(_RETRY_ATTEMPTS):
            try:
                LOGGER.debug("Fetching data from url: %s (Attempt %d)", url, attempt + 1)
                async with asyncio.timeout(20):
                    response = await self.session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                    )
                    response.raise_for_status()

                    self.connected = True
                    return await response.json()

            except TimeoutError as exception:
                LOGGER.error("Timeout error fetching information from %s: %s", url, exception)
                self.connected = False
                raise APITimeoutError(
                    "Timeout error fetching information",
                ) from exception

            except Exception as exception:  # pylint: disable=broad-except
                LOGGER.error("Unexpected error in _api_wrapper. URL: %s, Exception: %s", url, exception)
                self.connected = False
                raise APIConnectionError(
                    "Unexpected error in _api_wrapper",
                ) from exception

        return None

class APIConnectionError(Exception):
    """Exception class for connection error."""

class APITimeoutError(Exception):
    """Exception class for timeout error."""