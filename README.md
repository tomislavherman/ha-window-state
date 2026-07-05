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

## Sensor placement

This integration needs **two** contact sensors on the window. Both go on the
**moving edge of the window — the vertical side with the handle, opposite the
hinges.** Put one near the **top** and one near the **bottom** of that edge.

Do **not** mount the sensors on the hinge side: that edge barely moves when the
window opens, so the sensors there wouldn't detect anything. Position each
sensor so its two halves line up when the window is fully closed.

```
   hinges                    handle side (moving edge)
     │                                 │
     ▼                                 ▼
   ┌─────────────────────────────────[ TOP sensor ]┐
   │                                               │
   │                  window                       │
   │                                               │
   └──────────────────────────────[ BOTTOM sensor ]┘
```

Why top + bottom on the moving edge tells the three states apart:

| Window position                | Top sensor | Bottom sensor | Reported |
| ------------------------------ | ---------- | ------------- | -------- |
| Closed                         | closed     | closed        | `closed` |
| Tilted (handle up)             | open       | closed        | `tilted` |
| Open / turned (handle sideways)| open       | open          | `open`   |

When the window is **tilted**, it pivots along the bottom, so the top of the
moving edge swings in (top sensor opens) while the bottom stays put. When it's
**fully opened**, the whole moving edge swings in and both sensors open.

Tips:

- If a window reads `tilted` when it's actually closed (or vice-versa), your
  **top and bottom sensors are swapped** — fix it in the integration's
  **Configure** options, no remounting needed.
- A persistent `unknown` state (bottom open while top is closed) can't happen on
  a real tilt-and-turn window, so it usually means a **mis-mounted, misaligned,
  or failing bottom sensor**.

## Installation

### Don't have HACS yet?

HACS (Home Assistant Community Store) is not part of Home Assistant by default —
you have to add it once. If you don't see **HACS** in your sidebar, install it
first, then follow the custom-repository steps below. If you'd rather not use
HACS at all, skip to [Manual](#manual).

1. Open a terminal on your Home Assistant host (e.g. the **Terminal & SSH** or
   **Advanced SSH & Web Terminal** add-on from **Settings → Add-ons → Add-on
   Store**) and run:

   ```
   wget -O - https://get.hacs.xyz | bash -
   ```

2. **Restart Home Assistant** (**Settings → System →** power icon **→ Restart
   Home Assistant**).
3. Go to **Settings → Devices & Services → Add Integration**, search **HACS**,
   accept the prompts, and complete the **GitHub device login** it shows
   (open the link, enter the code, authorize). HACS then appears in your
   sidebar.

For the full, up-to-date procedure see the
[official HACS install docs](https://hacs.xyz/docs/use/download/download/).

### HACS (custom repository)

1. In Home Assistant, open **HACS** (from the sidebar).
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

## Options

Open the window's entry in **Settings → Devices & Services → Window State** and
choose **Configure** to:

- **Reselect the top and bottom sensors** after setup.
- **Hide source sensors** — hides the two contact sensors from the Home
  Assistant UI so only the derived window entity is shown. This works like the
  core Group helper's "Hide members": it hides them **everywhere**, not just
  under this window, and is reversed if you turn the option off or delete the
  window. Sensors you hid yourself are left untouched.

The window entity also lists its `top_sensor` and `bottom_sensor` as attributes,
so you can always see which sensors feed it from the entity's more-info dialog.
