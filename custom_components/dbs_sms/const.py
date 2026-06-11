"""Constants for the DBS SMS integration."""

DOMAIN = "dbs_sms"

CONF_PROVIDER = "provider"
CONF_DEFAULT_SENDER = "default_sender"

PROVIDER_HOSTEDSMS = "hostedsms"

# Supported SMS providers
PROVIDERS = {
    PROVIDER_HOSTEDSMS: "HostedSMS.pl",
}
