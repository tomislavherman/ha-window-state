# Brand assets

Source artwork for the Window State integration icon.

- `window_state.svg` — editable source (the "open" + "tilted" glyphs merged into
  an L-corner on a blue badge).
- `custom_integrations/window_state/icon.png` — 256×256, for submission.
- `custom_integrations/window_state/icon@2x.png` — 512×512 (hDPI).

Home Assistant does **not** load these from this repo. To make HA and HACS show
the icon, the two PNGs must be added to the
[home-assistant/brands](https://github.com/home-assistant/brands) repository
under `custom_integrations/window_state/` (this folder mirrors that path, so it
can be copied straight over). Until that PR is merged, HA shows the default
integration icon.
