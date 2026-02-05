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

# === Policy Rule Dictionary Keys ===
RULE_TYPE = "type"
RULE_DEFAULT = "default"
RULE_ERROR_MESSAGE = "error_message"

# === Rate Limit Keys ===
KEY_AI_GATEWAY = "ai_gateway"
KEY_RATE_LIMITS = "rate_limits"
KEY_KEY = "key"
KEY_USER = "user"
KEY_USER_GROUP = "user_group"
KEY_PRINCIPAL = "principal"
KEY_CALLS = "calls"
KEY_RENEWAL_PERIOD = "renewal_period"
TOKENS = "tokens"

# === Parsed/Computed Keys for Policy Engine ===
IS_RATE_LIMIT = "is_rate_limit"
KEY_NAME = "key_name"
RENEWAL_PERIOD = "renewal_period"
PRINCIPAL = "principal"
REQUESTS_PER_PREFIX = "requests_per_"

# === Common String Values ===
MINUTE = "minute"

# === Common Types ===
TYPE_REQUIRED = "required"
TYPE_FIXED = "fixed"

# === Other common strings can be added as needed ===
