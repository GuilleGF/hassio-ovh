# OVH DynHost Updater Component for Home Assistant

With the `ovh` integration you can keep your current IP address in sync with your [OVH DynHost](https://docs.ovh.com/ie/en/domains/hosting_dynhost/)  hostname or domain.  

To use the integration in your installation, add the following to your `configuration.yaml` file:

#### Configuration variables:
| Variable |  Required  |  Type  | Description |
| -------- | ---------- | ----------- | ----------- |
| `domain` | yes | string |  Your fully qualified domain name (FQDN) |
| `username` | yes | string | The generated username for this DDNS record |
| `password` | yes | string | The generated password for this DDNS record |
| `timeout` | no | integer | Timeout (in seconds) for the API calls (default: 10) |
#### Basic Example:

```yaml
ovh:
  domain: subdomain.domain.com
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
```