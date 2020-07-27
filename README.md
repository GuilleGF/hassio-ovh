# OVH DynHost Updater Component for Home Assistant

With the `ovh` integration you can keep your current IP address in sync with your [OVH DynHost](https://docs.ovh.com/ie/en/domains/hosting_dynhost/)  hostname or domain.  

To use the integration in your installation, add the following to your `configuration.yaml` file:

#### Configuration variables:
| Variable |  Required  |  Type  | Description |
| -------- | ---------- | ----------- | ----------- |
| `domain` | yes | string |  The subdomain you are modifying the DNS configuration for |
| `username` | yes | string | The DynHost username |
| `password` | yes | string | Password for the DynHost username |
#### Basic Example:

```yaml
ovh:
  domain: subdomain.domain.com
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
```
