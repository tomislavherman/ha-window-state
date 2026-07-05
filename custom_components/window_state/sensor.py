"""Sensor platform for Window State."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.restore_state import RestoreEntity

DOMAIN = "window_state"

CONF_NAME = "name"
CONF_TOP_SENSOR = "top_sensor"
CONF_BOTTOM_SENSOR = "bottom_sensor"

STATE_CLOSED = "closed"
STATE_TILTED = "tilted"
STATE_OPEN = "open"
STATE_WINDOW_UNKNOWN = "unknown"

WINDOW_STATES = [STATE_CLOSED, STATE_TILTED, STATE_OPEN, STATE_WINDOW_UNKNOWN]

_ICONS = {
    STATE_CLOSED: "mdi:window-closed-variant",
    STATE_TILTED: "mdi:window-open",
    STATE_OPEN: "mdi:window-open-variant",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Window State sensor from a config entry."""
    config = {**entry.data, **entry.options}
    async_add_entities([WindowStateSensor(entry, config)])


class WindowStateSensor(SensorEntity, RestoreEntity):
    """A sensor deriving tilt-and-turn window state from two contact sensors."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = WINDOW_STATES

    def __init__(self, entry: ConfigEntry, config: dict[str, str]) -> None:
        """Initialize the sensor."""
        self._top_entity_id = config[CONF_TOP_SENSOR]
        self._bottom_entity_id = config[CONF_BOTTOM_SENSOR]
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=config[CONF_NAME],
            manufacturer="Window State",
            model="Tilt-and-turn window",
        )

    async def async_added_to_hass(self) -> None:
        """Restore previous state and start listening for source changes."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in WINDOW_STATES:
                self._attr_native_value = last_state.state

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._top_entity_id, self._bottom_entity_id],
                self._handle_source_change,
            )
        )
        # Evaluate once now so we reflect current reality on startup.
        self._recalculate()

    @callback
    def _handle_source_change(self, event: Event[EventStateChangedData]) -> None:
        """React to a state change of either source sensor."""
        self._recalculate()

    @callback
    def _recalculate(self) -> None:
        """Recompute the window state and write it if it could be determined."""
        new_state = self._derive_state()
        # Keep the last known (possibly restored) value when a source is
        # temporarily unavailable, rather than dropping to "unknown".
        if new_state is not None:
            self._attr_native_value = new_state
        self.async_write_ha_state()

    @callback
    def _derive_state(self) -> str | None:
        """Map the two contact sensors to a window state.

        top=off, bottom=off -> closed
        top=on,  bottom=off -> tilted
        top=on,  bottom=on  -> open
        top=off, bottom=on  -> unknown (physically inconsistent)

        Returns None when either source is missing or unavailable.
        """
        top = self.hass.states.get(self._top_entity_id)
        bottom = self.hass.states.get(self._bottom_entity_id)
        if top is None or bottom is None:
            return None
        if top.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        if bottom.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        top_on = top.state == STATE_ON
        bottom_on = bottom.state == STATE_ON

        if not top_on and not bottom_on:
            return STATE_CLOSED
        if top_on and not bottom_on:
            return STATE_TILTED
        if top_on and bottom_on:
            return STATE_OPEN
        return STATE_WINDOW_UNKNOWN

    @property
    def icon(self) -> str:
        """Return an icon that reflects the current window state."""
        return _ICONS.get(self._attr_native_value, "mdi:window-closed")
