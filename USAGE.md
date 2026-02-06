# AI Gateway Policy Syntax and Usage Guide

This document explains how to design and write policies for the AI Gateway Policy Manager, including the syntax for rules, the use of regular expressions for endpoint selection, and practical examples. It is intended for anyone who wants to create or modify policies for Databricks model serving endpoints.

---

## Policy Structure

A policy is a JSON file with the following main sections:

- `policy_name`: A unique name for the policy.
- `policy_version`: The version of the policy.
- `description`: A human-readable description.
- `applies_to`: Criteria for which endpoints the policy applies to (supports regex).
- `rules`: A dictionary of policy rules to enforce.

### Example
```json
{
  "policy_name": "disabled-serving-policy",
  "policy_version": "1.0",
  "description": "Policy that disables the endpoint by setting the rate limit to 0",
  "applies_to": {
    "serving_endpoint_name": "^databricks-.*"
  },
  "rules": {
    "ai_gateway.rate_limits": {
      "type": "required",
      "error_message": "AI Gateway must be present even if the endpoint is disabled"
    },
    "ai_gateway.rate_limits.user.requests_per_minute": {
      "type": "fixed",
      "default": 0,
      "error_message": "Rate limit is set to 0 (endpoint disabled)"
    }
  }
}
```

---

## `applies_to` Syntax (Endpoint Selection)

- The `applies_to` field uses regular expressions to match endpoint names.
- Example: `{ "serving_endpoint_name": "^databricks-.*" }` applies the policy to all endpoints whose name starts with `databricks-`.
- You can use any valid Python regex pattern.

### Regex Examples
| Pattern                | Matches Example Endpoint Names         |
|------------------------|---------------------------------------|
| `^databricks-.*`       | `databricks-prod`, `databricks-test`  |
| `.*-prod$`             | `api-prod`, `databricks-prod`         |
| `^test-.*|.*-dev$`     | `test-foo`, `bar-dev`                 |

---

## Rules Syntax


Each rule is a key-value pair under `rules`. The key uses dot notation to specify the config path. Supported syntaxes for rate limit rules:

### Supported Rate Limit Rule Key Patterns

- `ai_gateway.rate_limits.user.requests_per_minute`: Applies to the default user rate limit.
- `ai_gateway.rate_limits.user_group.<group>.requests_per_minute`: Applies to a specific user group (e.g., `user_group.AZ_DATAANALYTICSRDPRE_LKHSRD_Oper`).
- `ai_gateway.rate_limits.principal.<name>.requests_per_minute`: Applies to a specific principal (e.g., `principal.uami_pepe`).

### 1. Required Key
```json
"ai_gateway.rate_limits": {
  "type": "required",
  "error_message": "AI Gateway must be present"
}
```
- Ensures the key exists in the endpoint config.

### 2. Fixed Value
```json
"ai_gateway.rate_limits.user.requests_per_minute": {
  "type": "fixed",
  "default": 0,
  "error_message": "Rate limit must be 0"
}
```
- Ensures the value is exactly as specified by `default`. If not, it will be corrected.


### 3. Rate Limit Rules
Keys like the following are parsed specially and will create or update the corresponding rate limit entry in the endpoint config:

#### User Rate Limit
```json
"ai_gateway.rate_limits.user.requests_per_minute": {
  "type": "fixed",
  "default": 0,
  "error_message": "Rate limit is set to 0 (endpoint disabled)"
}
```

#### User Group Rate Limit
```json
"ai_gateway.rate_limits.user_group.AZ_DATAANALYTICSRDPRE_LKHSRD_Oper.requests_per_minute": {
  "type": "fixed",
  "default": 0,
  "error_message": "Rate limit is set to 0 (endpoint disabled)"
}
```

#### Principal Rate Limit
```json
"ai_gateway.rate_limits.principal.uami_pepe.requests_per_minute": {
  "type": "fixed",
  "default": 0,
  "error_message": "Rate limit is set to 0 (endpoint disabled)"
}
```

These rules will ensure the corresponding rate limit entry is present in the endpoint configuration, with the correct `key` and `principal` fields as needed.

---

## Writing Regex for Endpoint Selection

- Use `^` to match the start, `$` for the end, `.*` for any characters.
- Combine patterns with `|` for OR logic.
- Test your regex with online tools (e.g., regex101.com) or Python's `re` module.

### More Examples
| Regex Pattern         | Description                                 |
|----------------------|---------------------------------------------|
| `^api-.*`            | All endpoints starting with `api-`          |
| `.*-staging$`        | All endpoints ending with `-staging`        |
| `^prod-.*|.*-prod$`  | Endpoints starting or ending with `prod-`   |

---

## Full Example Policy

```json
{
  "policy_name": "disabled-serving-policy",
  "policy_version": "1.0",
  "description": "Policy que deshabilita completamente el endpoint fijando el rate limit a 0",
  "applies_to": {
    "serving_endpoint_name": "^databricks-.*"
  },
  "rules": {
    "ai_gateway.rate_limits": {
      "type": "required",
      "error_message": "El AI Gateway debe estar presente aunque el endpoint esté deshabilitado"
    },
    "ai_gateway.rate_limits.user.requests_per_minute": {
      "type": "fixed",
      "default": 0,
      "error_message": "El rate limit está fijado a 0 (endpoint deshabilitado)"
    },
    "ai_gateway.rate_limits.user_group.AZ_DATAANALYTICSRDPRE_LKHSRD_Oper.requests_per_minute": {
      "type": "fixed",
      "default": 0,
      "error_message": "El rate limit está fijado a 0 (endpoint deshabilitado)"
    },
    "ai_gateway.rate_limits.principal.uami_pepe.requests_per_minute": {
      "type": "fixed",
      "default": 0,
      "error_message": "El rate limit está fijado a 0 (endpoint deshabilitado)"
    }
  }
}
```

---

## Tips
- Always provide clear `error_message` fields for easier debugging.
- Use descriptive `policy_name` and `description`.
- Test your regex patterns before deploying policies.
- You can define as many rules as needed under `rules`.

---

## PolicyManager: High-Level API Usage

The `PolicyManager` class provides a high-level interface for loading, validating, and applying policies to Databricks endpoints. You can use it to apply a policy to a single endpoint or to multiple endpoints in bulk, as well as to generate compliance reports.

### Basic Usage Example

```python
from custom_ai_gateway_policies.manager import PolicyManager

# Initialize the manager
manager = PolicyManager()

# Load a policy from a JSON file or dictionary
policy = manager.load_policy("policy.json")

# Apply the policy to a specific endpoint (dry-run mode)
result = manager.apply_policy("my-endpoint", policy, dry_mode=True)
if not result.is_compliant:
    print(f"Violations found: {len(result.errors)}")
    for err in result.errors:
        print(f"- {err.key}: {err.message}")
else:
    print("Endpoint is compliant with the policy")
```

### Apply a Policy to Multiple Endpoints (Bulk)

```python
# You can filter endpoints using a regex dictionary (e.g., by name)
bulk_results = manager.apply_policy_bulk(policy, filter_dict={"name": "^databricks-.*"}, dry_mode=True)
for res in bulk_results:
    print(f"Endpoint: {res.endpoint_name}, Compliant: {res.is_compliant}")
    if not res.is_compliant:
        for err in res.errors:
            print(f"  - {err.key}: {err.message}")
```

### Apply Real Corrections (Not Dry-Run)

```python
# To actually apply corrections to the endpoints:
result = manager.apply_policy("my-endpoint", policy, dry_mode=False)
# Or in bulk mode:
bulk_results = manager.apply_policy_bulk(policy, dry_mode=False)
```

### Generate a Compliance Report

```python
report = manager.get_compliance_report(bulk_results)
print(report)
# Example output:
# {
#   'total_endpoints': 3,
#   'compliant': 2,
#   'non_compliant': 1,
#   'compliance_rate': 0.666,
#   'total_violations': 2,
#   'violations': [
#       {'endpoint': 'databricks-prod', 'key': 'ai_gateway.rate_limits.user.requests_per_minute', 'message': 'Rate limit must be 0'}
#   ]
# }
```

### Main Methods of PolicyManager

- `load_policy(policy_source)`: Loads and validates a policy from a file or dictionary.
- `apply_policy(endpoint_name, policy, dry_mode=True)`: Applies the policy to a single endpoint. If `dry_mode` is `False`, corrections are applied.
- `apply_policy_bulk(policy, filter_dict=None, dry_mode=True)`: Applies the policy to all endpoints matching the filter (or all if no filter is specified).
- `get_compliance_report(results)`: Generates a summary report from a list of policy results.

> **Note:** All methods return `PolicyResult` objects or lists of them, containing information about compliance, proposed/applied corrections, and any errors found.

---

For more examples, see the `PolicyManager` class docstring or review the tests in the `tests/` folder.
