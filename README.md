# OVH DynHost Updater Component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

With the `ovh` integration you can keep your current IP address in sync with your [OVH DynHost](https://docs.ovh.com/ie/en/domains/hosting_dynhost/)  hostname or domain.  

[![Opens your Home Assistant instance and adds a repository to the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GuilleGF&repository=hassio-ovh&category=integration)

To use the integration in your installation, add the following to your `configuration.yaml` file:

The configuration accepts a list of entries, so you can manage multiple DynHost records with different credentials independently.

#### Configuration variables:
| Variable |  Required  |  Type  | Description |
| -------- | ---------- | ----------- | ----------- |
| `domain` | yes | string | The subdomain you are updating the DNS configuration for |
| `username` | yes | string | The DynHost username |
| `password` | yes | string | Password for the DynHost username |
| `scan_interval` | no | time | How often to call the update service. (default: 15 minutes) |

#### Example:

```yaml
ovh:
  - domain: subdomain.domain.com
    username: YOUR_USERNAME
    password: YOUR_PASSWORD

  - domain: other.domain.com
    username: OTHER_USERNAME
    password: OTHER_PASSWORD
    scan_interval: 00:30:00
```
Based on the official [No-IP.com](https://github.com/home-assistant/core/tree/dev/homeassistant/components/no_ip) and [Mythic Beasts](https://github.com/home-assistant/core/blob/dev/homeassistant/components/mythicbeastsdns) integrations. Thanks to the creators!
