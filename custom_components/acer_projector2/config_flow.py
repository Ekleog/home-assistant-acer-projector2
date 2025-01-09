"""Adds config flow for Acer Projector v2."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_FILENAME
from homeassistant.helpers import selector

from .const import DOMAIN


class AcerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Acer projectors."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_FILENAME], data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FILENAME,
                        default=(user_input or {}).get(CONF_FILENAME, "/dev/ttyUSB0"),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )
