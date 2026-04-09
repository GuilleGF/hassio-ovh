"""Constants for OVH DynHost integration."""

from datetime import timedelta

DOMAIN = "ovh"
CONF_IPV6 = "ipv6"

DEFAULT_INTERVAL = timedelta(minutes=15)

TIMEOUT = 30
HOST = "dns.eu.ovhapis.com/nic/update"
IP_RESOLVER_V4 = "https://api4.ipify.org"
IP_RESOLVER_V6 = "https://api6.ipify.org"

OVH_ERRORS = {
    "nohost": "Hostname supplied does not exist under specified account",
    "badauth": "Invalid username password combination",
    "badagent": "Client disabled",
    "!donator": "An update request was sent with a feature that is not available",
    "abuse": "Username is blocked due to abuse",
}
