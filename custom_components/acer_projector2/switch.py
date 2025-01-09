"""Switch platform for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import timedelta

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import CONF_FILENAME

import serial_asyncio_fast as serial_asyncio
import asyncio

from custom_components.acer_projector2.const import LOGGER


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="acer_projector2",
        name="Acer Projector",
        icon="mdi:projector",
    ),
)

SCAN_INTERVAL = timedelta(seconds=10)

async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: dict,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        IntegrationAcerSwitch(
            config = entry,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )

class IntegrationAcerSwitch(SwitchEntity):
    """integration_blueprint switch class."""

    async def _execute(self, cmd: str) -> str:
        url = self.config.get(CONF_FILENAME, "")
        for retry in range(3):
            reader, writer = await serial_asyncio.open_serial_connection(
                url = url,
                baudrate = 9600,
                bytesize = serial_asyncio.serial.EIGHTBITS,
                parity = serial_asyncio.serial.PARITY_NONE,
                stopbits = serial_asyncio.serial.STOPBITS_ONE,
                xonxoff = False,
                rtscts = False,
                dsrdtr = False,
            )
            writer.write(cmd.encode("utf-8"))
            try:
                resp = await asyncio.wait_for(reader.readuntil(b'\r'), timeout=5)
                return resp.decode("utf-8")
            except asyncio.TimeoutError:
                continue
        raise RuntimeError("Projector at " + url + " did not respond")

    def __init__(
        self,
        config: dict,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the projector class."""
        super().__init__()
        self.config = config
        self.entity_description = entity_description
        self.attr_is_on = False

    @property
    def is_on(self) -> bool:
        """Return true if the projector is on."""
        return self.attr_is_on

    async def async_update(self) -> None:
        """Update the state of the projector."""
        resp = await self._execute("* 0 Lamp ?\r")
        LOGGER.debug("Projector response: %s", repr(resp))
        self.attr_is_on = resp[-2:] == "1\r"

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self._execute("* 0 IR 001\r")

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self._execute("* 0 IR 002\r")
