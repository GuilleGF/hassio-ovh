# OVH DynHost Updater Component for Home Assistant

[![GitHub Release](https://img.shields.io/github/release/GuilleGF/hassio-ovh.svg)](https://GitHub.com/GuilleGF/hassio-ovh/releases/)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/GuilleGF/hassio-ovh/actions/workflows/validate.yaml/badge.svg)](https://github.com/GuilleGF/hassio-ovh/actions/workflows/validate.yaml)
[![Lint](https://github.com/GuilleGF/hassio-ovh/actions/workflows/lint.yaml/badge.svg)](https://github.com/GuilleGF/hassio-ovh/actions/workflows/lint.yaml)
[![HA integration usage](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=Integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ovh.total)](https://analytics.home-assistant.io/custom_integrations.json)


With the `ovh` integration you can keep your current IP address in sync with your [OVH DynHost](https://docs.ovh.com/gb/en/domains/hosting_dynhost/) hostname or domain.

## Installation

[![Open your Home Assistant instance and add a custom HACS repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GuilleGF&repository=hassio-ovh&category=integration)

Install via HACS, then restart Home Assistant.

## Prerequisites

Before configuring this integration, you need to set up a DynHost record in your OVH control panel:

1. Log in to the [OVH Control Panel](https://www.ovh.com/manager/)
2. Go to **Web Cloud → Domain names → your domain → DynHost**
3. Create a DynHost record for the subdomain you want to keep updated
4. Create a DynHost access login with a username and password for that record

> The **username** will be in the format `yourdomain.com-identifier` and the **password** is set when creating the DynHost access. These are the credentials you will need below.

## Configuration

After installation and restart, you can configure the integration from the UI:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ovh)

Or go to **Settings → Devices & Services → Add Integration** and search for **OVH DynHost**.

You can add multiple entries — one per domain — each with independent credentials and update settings.

### Configuration variables

| Variable | Required | Type | Description |
| -------- | -------- | ---- | ----------- |
| `domain` | yes | string | The full hostname to update (e.g. `sub.example.com`) |
| `username` | yes | string | The DynHost username |
| `password` | yes | string | Password for the DynHost username |
| `ipv6` | no | boolean | Use IPv6 instead of IPv4 (default: `false`). Editable after setup. |
| `scan_interval` | no | integer (seconds) | How often to update the DNS record (default: `900`). Editable after setup. |

## YAML configuration (legacy)

YAML configuration is still supported for backwards compatibility. Existing YAML entries are automatically imported as UI config entries on first startup with this version.

Single entry format (without `-`) is also supported.

```yaml
ovh:
  - domain: subdomain.domain.com
    username: YOUR_USERNAME
    password: YOUR_PASSWORD

  - domain: other.domain.com
    username: OTHER_USERNAME
    password: OTHER_PASSWORD
    scan_interval: 1800
    ipv6: true
```

---

Based on the official [No-IP.com](https://github.com/home-assistant/core/tree/dev/homeassistant/components/no_ip) and [Mythic Beasts](https://github.com/home-assistant/core/blob/dev/homeassistant/components/mythicbeastsdns) integrations. Thanks to the creators!
