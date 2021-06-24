# OVH DynHost Updater Component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

With the `ovh` integration you can keep your current IP address in sync with your [OVH DynHost](https://docs.ovh.com/ie/en/domains/hosting_dynhost/)  hostname or domain.  

To use the integration in your installation, add the following to your `configuration.yaml` file:

#### Configuration variables:
| Variable |  Required  |  Type  | Description |
| -------- | ---------- | ----------- | ----------- |
| `domain` | yes | string |  The subdomain/subdomains you are modifying the DNS configuration for |
| `username` | yes | string | The DynHost username |
| `password` | yes | string | Password for the DynHost username |
| `scan_interval` | no |  time | How often to call the update service  (seconds). (default: 10 minutes) |

#### Basic Example:

```yaml
ovh:
  domain: subdomain.domain.com
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
```

Suports multiple subdomains separated by a comma if they all use the same DynHost username and password.
```yaml
ovh:
  domain: "subdomain1.domain.com,subdomain2.domain.com"
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
  scan_interval: 300
```
Based on the official [No-IP.com](https://github.com/home-assistant/core/tree/dev/homeassistant/components/no_ip) and [Mythic Beasts](https://github.com/home-assistant/core/blob/dev/homeassistant/components/mythicbeastsdns) integrations. Thanks to the creators!
