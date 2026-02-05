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

Each rule is a key-value pair under `rules`. The key uses dot notation to specify the config path. Supported rule types:

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
- Keys like `ai_gateway.rate_limits.<key>.requests_per_minute` are parsed specially.
- Example:
```json
"ai_gateway.rate_limits.user.requests_per_minute": {
  "type": "fixed",
  "default": 100,
  "error_message": "User rate limit must be 100"
}
```
- This enforces that the `user` rate limit is set to 100 requests per minute.

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
  "policy_name": "strict-prod-policy",
  "policy_version": "1.1",
  "description": "Production endpoints must have strict rate limits",
  "applies_to": {
    "serving_endpoint_name": ".*-prod$"
  },
  "rules": {
    "ai_gateway.rate_limits": {
      "type": "required",
      "error_message": "AI Gateway config required"
    },
    "ai_gateway.rate_limits.user.requests_per_minute": {
      "type": "fixed",
      "default": 100,
      "error_message": "User rate limit must be 100"
    },
    "ai_gateway.rate_limits.admin.requests_per_minute": {
      "type": "fixed",
      "default": 1000,
      "error_message": "Admin rate limit must be 1000"
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

For more advanced usage, see the example policies in the `example/` folder.
