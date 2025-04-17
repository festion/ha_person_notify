"""Constants for the Person-Based Notification System integration."""

DOMAIN = "person_notify"

# Severity levels
SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITIES = [SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_CRITICAL]

# Notification preferences
PREF_ALL_DEVICES = "all_devices"
PREF_MOBILE_ONLY = "mobile_only"
PREF_DESKTOP_ONLY = "desktop_only"
PREF_LOG_ONLY = "log_only"
PREF_NONE = "none"

PREFERENCES = [PREF_ALL_DEVICES, PREF_MOBILE_ONLY, PREF_DESKTOP_ONLY, PREF_LOG_ONLY, PREF_NONE]

# Config keys
CONF_PERSON = "person"
CONF_SEVERITY = "severity"
CONF_TITLE = "title"
CONF_MESSAGE = "message"

# Service name
SERVICE_NOTIFY_PERSON = "notify_person"