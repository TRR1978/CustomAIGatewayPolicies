# Pandas DataFrame output format
RECORDS = "records"

"""
Constants for policy engine keys and values.
Grouped for clarity and maintainability.
"""

# === General Field Keys ===
FIELD = "field"
NAME = "name"  # For endpoint name filtering
SERVING_ENDPOINT_NAME = "serving_endpoint_name"
RULES = "rules"  # Key for rules in policy dict
APPLIES_TO = "applies_to"  # Key for filter criteria in policy dict
POLICY_NAME = "policy_name"  # Key for policy name in policy dict
POLICY_VERSION = "policy_version"  # Key for policy version in policy dict

REQUIRED_POLICY_FIELDS = [POLICY_NAME, POLICY_VERSION, RULES]


# === Policy Rule Dictionary Keys ===
RULE_TYPE = "type"
RULE_DEFAULT = "default"
RULE_ERROR_MESSAGE = "error_message"

# === Rate Limit Keys ===
KEY_AI_GATEWAY = "ai_gateway"
KEY_RATE_LIMITS = "rate_limits"
KEY_FALLBACK_CONFIG = "fallback_config"
KEY_USAGE_TRACKING_CONFIG = "usage_tracking_config"
KEY_KEY = "key"
KEY_USER = "user"
KEY_USER_GROUP = "user_group"
KEY_PRINCIPAL = "principal"
KEY_CALLS = "calls"
KEY_RENEWAL_PERIOD = "renewal_period"
KEY_NAME = "key_name"
TOKENS = "tokens"

# === Parsed/Computed Keys for Policy Engine ===
IS_RATE_LIMIT = "is_rate_limit"
RENEWAL_PERIOD = "renewal_period"
PRINCIPAL = "principal"
REQUESTS_PER_PREFIX = "requests_per_"
ENABLED = "enabled"

# === Common String Values ===
MINUTE = "minute"

# === Common Types ===
TYPE_REQUIRED = "required"
TYPE_FIXED = "fixed"

TYPE_VALUES = [TYPE_REQUIRED, TYPE_FIXED]

# === Other common strings can be added as needed ===
