"""Config and options flow for Window State."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
)

DOMAIN = "window_state"

CONF_NAME = "name"
CONF_TOP_SENSOR = "top_sensor"
CONF_BOTTOM_SENSOR = "bottom_sensor"
CONF_HIDE_SOURCES = "hide_source_sensors"

_SENSOR_SELECTOR = EntitySelector(EntitySelectorConfig(domain="binary_sensor"))


class WindowStateConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Window State."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: add a single window."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=user_input
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): TextSelector(),
                vol.Required(CONF_TOP_SENSOR): _SENSOR_SELECTOR,
                vol.Required(CONF_BOTTOM_SENSOR): _SENSOR_SELECTOR,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return WindowStateOptionsFlow()


class WindowStateOptionsFlow(OptionsFlow):
    """Allow editing the source sensors after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_TOP_SENSOR, default=current[CONF_TOP_SENSOR]
                ): _SENSOR_SELECTOR,
                vol.Required(
                    CONF_BOTTOM_SENSOR, default=current[CONF_BOTTOM_SENSOR]
                ): _SENSOR_SELECTOR,
                vol.Required(
                    CONF_HIDE_SOURCES,
                    default=current.get(CONF_HIDE_SOURCES, False),
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
