# Window State

A Home Assistant custom integration that derives a single **window state** sensor
from the two contact (reed) sensors on a tilt-and-turn window — one at the top
(tilt) and one at the bottom (open).

Each configured window becomes its own device with one enum sensor entity.

## State logic

| Top contact | Bottom contact | Window state |
| ----------- | -------------- | ------------ |
| `off`       | `off`          | `closed`     |
| `on`        | `off`          | `tilted`     |
| `on`        | `on`           | `open`       |
| `off`       | `on`           | `unknown`    |

The `off/on` combination is physically inconsistent for a tilt-and-turn window,
so it is reported as `unknown`. When a source sensor is unavailable the sensor
keeps its last known state (and is restored across restarts).

The sensor is a `device_class: enum` sensor with the options
`closed`, `tilted`, `open`, `unknown`. It updates reactively (local push) the
moment either source sensor changes — no polling.

## Installation

### HACS (custom repository)

1. In Home Assistant, open **HACS → Integrations**.
2. Click the **⋮** menu (top right) → **Custom repositories**.
3. Add `https://github.com/tomislavherman/ha-window-state` with category
   **Integration**.
4. Search for **Window State**, install it, and **restart Home Assistant**.

### Manual

1. Copy `custom_components/window_state` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

This integration is configured entirely through the UI — there is no YAML.

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Window State**.
3. Enter a **Name**, then pick the **Top contact sensor** and
   **Bottom contact sensor** (the pickers are filtered to `binary_sensor`
   entities).
4. Submit. A new device and its window-state sensor are created.

Repeat **Add Integration** for each window you want to track — multiple
instances are supported.

To change the source sensors later, open the integration entry and choose
**Configure** to reselect the top and bottom sensors.
