"""The Window State integration."""

from __future__ import annotations

from collections.abc import Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

DOMAIN = "window_state"
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_TOP_SENSOR = "top_sensor"
CONF_BOTTOM_SENSOR = "bottom_sensor"
CONF_HIDE_SOURCES = "hide_source_sensors"


@callback
def _source_entity_ids(entry: ConfigEntry) -> set[str]:
    """Return the two source sensor entity ids for this window."""
    config = {**entry.data, **entry.options}
    return {config[CONF_TOP_SENSOR], config[CONF_BOTTOM_SENSOR]}


@callback
def _set_hidden(hass: HomeAssistant, entity_ids: Iterable[str], hidden: bool) -> None:
    """Hide or unhide entities in the registry.

    Hiding a source affects it everywhere in Home Assistant (same as the core
    Group helper's "Hide members"). We only ever unhide entities we hid
    ourselves, so anything the user hid manually is left untouched.
    """
    registry = er.async_get(hass)
    for entity_id in entity_ids:
        entity = registry.async_get(entity_id)
        if entity is None:
            continue
        if hidden and entity.hidden_by is None:
            registry.async_update_entity(
                entity_id, hidden_by=er.RegistryEntryHider.INTEGRATION
            )
        elif not hidden and entity.hidden_by is er.RegistryEntryHider.INTEGRATION:
            registry.async_update_entity(entity_id, hidden_by=None)


@callback
def _async_apply_visibility(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reconcile source-sensor visibility with the current options.

    Tracks the exact set we hid (per entry) so that toggling the option off or
    changing the source sensors reliably restores the previously hidden ones.
    """
    store: dict[str, set[str]] = hass.data.setdefault(DOMAIN, {})
    previously_hidden = store.get(entry.entry_id, set())

    config = {**entry.data, **entry.options}
    want_hidden = config.get(CONF_HIDE_SOURCES, False)
    sources = _source_entity_ids(entry)
    should_hide = sources if want_hidden else set()

    # Unhide anything we previously hid that should no longer be hidden.
    _set_hidden(hass, previously_hidden - should_hide, False)
    _set_hidden(hass, should_hide, True)
    store[entry.entry_id] = should_hide


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Window State from a config entry."""
    _async_apply_visibility(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Restore visibility of any sources we hid when the window is deleted."""
    store: dict[str, set[str]] = hass.data.setdefault(DOMAIN, {})
    _set_hidden(hass, store.pop(entry.entry_id, set()), False)
