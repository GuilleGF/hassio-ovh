# Changelog

## [3.1.0] - 2026-04-09

### Added

- UI configuration flow: integration can now be set up from **Settings → Devices & Services** without editing YAML
- Support for multiple domains via repeated "Add integration" — each entry is managed independently
- Options flow to edit `ipv6` and `scan_interval` after initial setup without recreating the entry
- Translations for English (`en`), Spanish (`es`), and French (`fr`)
- `const.py` module to centralise shared constants

### Changed

- YAML configuration is now imported automatically as UI config entries on first startup — no manual migration needed
- `scan_interval` is stored in seconds (integer) in the options flow; YAML `time_period` values are converted automatically on import
- Manifest version bumped to `3.1.0`; added `config_flow: true` and `integration_type: service`

---

## [3.0.0] - 2026-04-09

### Breaking changes

- Configuration format changed to list-based entries. Single entry format (without `-`) is still supported for backwards compatibility.

  **New format:**
  ```yaml
  ovh:
    - domain: subdomain.domain.com
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
  ```

  **Old format (still works):**
  ```yaml
  ovh:
    domain: subdomain.domain.com
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
  ```

### Added

- Support for multiple DynHost entries with independent credentials
- IPv6 support via optional `ipv6: true` config flag (uses `api6.ipify.org` to resolve the public IPv6 address)
- External public IP resolution via [ipify.org](https://www.ipify.org) before each update
- Graceful error handling when IP resolution fails (skips update and logs a warning)
- Unit tests covering config schema validation and all integration functions

### Changed

- `myip` parameter is now explicitly sent to the OVH API with the resolved public IP
- Manifest version bumped to `3.0.0`
- CI workflows modernized: pinned action SHAs, merged hassfest + HACS into a single validate workflow, added Ruff linter and formatter

---

## [2.0.0] - 2023-xx-xx

### Changed

- Removed HTTP basic auth from OVH API requests
- Trim whitespace from `domain`, `username`, and `password` config values

---

## [1.x]

- Initial releases with single-host DynHost support, configurable scan interval, and timeout handling
