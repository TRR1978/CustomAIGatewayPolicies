"""Core policy engine for validating and applying policies to endpoint configurations."""


from typing import Dict, Tuple, Any, List
import logging

from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError
from custom_ai_gateway_policies.constants import (
    RULE_TYPE, RULE_DEFAULT, RULE_ERROR_MESSAGE, NAME,
    KEY_AI_GATEWAY, KEY_RATE_LIMITS, KEY_USER, KEY_USER_GROUP, KEY_PRINCIPAL, KEY_CALLS, KEY_RENEWAL_PERIOD,
    TYPE_REQUIRED, TYPE_FIXED, FIELD, KEY_NAME, IS_RATE_LIMIT, REQUESTS_PER_PREFIX, MINUTE, KEY_KEY
)

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Engine for validating and applying policies to endpoint configurations."""

    @staticmethod
    def parse_rate_limit_key(policy_key: str) -> Dict[str, Any]:
        """
        Parse a policy key into components for rate limit manipulation.

        Supports keys like:
        - ai_gateway.rate_limits.user.requests_per_minute
        - ai_gateway.rate_limits.user_group.<group>.requests_per_minute
        - ai_gateway.rate_limits.principal.<principal>.requests_per_minute

        Args:
            policy_key (str): Policy key in dot notation

        Returns:
            Dict[str, Any]: Parsed components (is_rate_limit, key_name, principal, field, renewal_period)
        """
        parts = policy_key.split('.')
        return_value = {}
        if len(parts) >= 4 and parts[0] == KEY_AI_GATEWAY and parts[1] == KEY_RATE_LIMITS:
            return_value[IS_RATE_LIMIT] = True
            if parts[2] == KEY_USER and len(parts) == 4:
                return_value[KEY_NAME] = parts[2]
                return_value[FIELD] = parts[3]
            elif parts[2] in (KEY_USER_GROUP, KEY_PRINCIPAL) and len(parts) >= 5:
                return_value[KEY_NAME] = parts[2]
                return_value[KEY_PRINCIPAL] = parts[3]
                return_value[FIELD] = parts[4]
            else:
                return_value[KEY_NAME] = parts[2]
                return_value[FIELD] = parts[3]

            if return_value[FIELD].startswith(REQUESTS_PER_PREFIX):
                renewal_period = return_value[FIELD].replace(REQUESTS_PER_PREFIX, "")
            else:
                renewal_period = MINUTE

            return_value[KEY_RENEWAL_PERIOD] = renewal_period
        else:
            return_value[IS_RATE_LIMIT] = False
        return return_value

    @staticmethod
    def search_nested_key(data: Dict[str, Any], key: str) -> Tuple[bool, Any]:
        """
        Search for a nested key in a dictionary using dot notation.

        Args:
            data (Dict[str, Any]): Dictionary to search
            key (str): Key in dot notation (e.g., 'config.rate_limit')

        Returns:
            Tuple[bool, Any]: (exists, value) where exists is True if key found
        """
        keys = key.split(".")
        current = data
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False, None
        if isinstance(current, dict) and keys[-1] in current:
            return True, current[keys[-1]]
        return False, None

    def apply_policy(
        self,
        policy_name: str,
        policy_rules: Dict[str, Dict[str, Any]],
        endpoint_config: Dict[str, Any]
    ) -> PolicyResult:
        """
        Apply policy rules to an endpoint configuration.

        Always applies corrections. Use dry_mode at a higher level to control
        whether corrected_config is actually applied to the endpoint.

        Args:
            policy_name (str): Name of the policy being applied (for reporting)
            policy_rules (Dict[str, Dict[str, Any]]): Dictionary of policy rules
            endpoint_config (Dict[str, Any]): Endpoint configuration to validate

        Returns:
            PolicyResult: Validation results and corrected configuration

        Raises:
            ValueError: If policy_rules or endpoint_config is invalid
        """
        if not isinstance(policy_rules, dict):
            raise ValueError("policy_rules must be a dictionary")
        if not isinstance(endpoint_config, dict):
            raise ValueError("endpoint_config must be a dictionary")

        endpoint_name = endpoint_config.get(NAME)

        errors: List[ValidationError] = []
        corrected_config = endpoint_config.copy()

        logger.info(f"Applying {len(policy_rules)} policy rules")

        for policy_key, rule in policy_rules.items():
            try:
                self._apply_single_rule(
                    policy_key=policy_key,
                    rule=rule,
                    corrected_config=corrected_config,
                    errors=errors
                )
            except Exception as e:
                logger.error(f"Error applying rule {policy_key}: {e}")
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"Internal error: {str(e)}"
                ))

        is_compliant = len(errors) == 0
        logger.info(f"Policy application complete. Compliant: {is_compliant}, Errors: {len(errors)}")

        return PolicyResult(
            is_compliant=is_compliant,
            corrected_config=corrected_config,
            errors=errors,
            endpoint_name=endpoint_name,
            policy_name=policy_name
        )

    def _apply_single_rule(
        self,
        policy_key: str,
        rule: Dict[str, Any],
        corrected_config: Dict[str, Any],
        errors: List['ValidationError']
    ) -> None:
        """
        Internal method to apply a single policy rule to the configuration.

        Args:
            policy_key (str): The policy key to apply
            rule (Dict[str, Any]): The rule definition
            corrected_config (Dict[str, Any]): The config to correct
            errors (List[ValidationError]): List to append errors to
        """
        rule_type = rule.get(RULE_TYPE)
        default = rule.get(RULE_DEFAULT)
        error_message = rule.get(RULE_ERROR_MESSAGE, f"Policy violation for {policy_key}")

        parsed = self.parse_rate_limit_key(policy_key)

        if parsed[IS_RATE_LIMIT]:
            self._apply_rate_limit_rule(
                policy_key=policy_key,
                rule_type=rule_type,
                default=default,
                error_message=error_message,
                parsed=parsed,
                corrected_config=corrected_config,
                errors=errors
            )
        else:
            self._apply_generic_rule(
                policy_key=policy_key,
                rule_type=rule_type,
                default=default,
                error_message=error_message,
                corrected_config=corrected_config,
                errors=errors
            )

    def _find_rate_limit_entry(self,
                               rate_limits: List[Dict[str, Any]],
                               key_name: str, principal: str = None) -> Tuple[Any, Any]:
        """
        Find the specific rate limit entry by key and optionally principal.

        Args:
            rate_limits (List[Dict[str, Any]]): List of rate limit dicts
            key_name (str): The key to match
            principal (str, optional): The principal to match (if any)

        Returns:
            Tuple[limit_entry, limit_index]: The found entry and its index, or (None, None)
        """
        limit_entry = None
        limit_index = None
        for idx, limit in enumerate(rate_limits):
            # Determine the key to check and the value to match
            if key_name == KEY_PRINCIPAL:
                key_to_check = KEY_PRINCIPAL
                value_to_match = principal
            else:
                key_to_check = KEY_KEY
                value_to_match = key_name

            if limit.get(key_to_check) == value_to_match:
                limit_entry = limit
                limit_index = idx
                break
        return limit_entry, limit_index

    def _set_rate_limit(self,
                        key_name: str,
                        default: Any,
                        renewal_period: str,
                        principal: str = None) -> Dict[str, Any]:
        """
        Create a rate limit dictionary for insertion into the config.

        Args:
            key_name (str): The key for the rate limit
            default (Any): The value for 'calls'
            renewal_period (str): The renewal period
            principal (str, optional): The principal, if any

        Returns:
            Dict[str, Any]: The rate limit entry
        """
        rate_limit = {}
        rate_limit[KEY_NAME] = key_name
        rate_limit[KEY_CALLS] = default
        rate_limit[KEY_RENEWAL_PERIOD] = renewal_period
        if principal is not None:
            rate_limit[KEY_PRINCIPAL] = principal
        return rate_limit

    def _apply_rate_limit_rule(
        self,
        policy_key: str,
        rule_type: str,
        default: Any,
        error_message: str,
        parsed: Dict[str, Any],
        corrected_config: Dict[str, Any],
        errors: List['ValidationError']
    ) -> None:
        """
        Internal method to apply a rate limit rule to the configuration.

        Args:
            policy_key (str): The policy key
            rule_type (str): The type of rule ('required', 'fixed', etc.)
            default (Any): The default value to enforce
            error_message (str): Error message to use
            parsed (Dict[str, Any]): Parsed key info
            corrected_config (Dict[str, Any]): Config to correct
            errors (List[ValidationError]): List to append errors to
        """
        key_name = parsed.get(KEY_NAME)
        principal = parsed.get(KEY_PRINCIPAL)
        renewal_period = parsed.get(KEY_RENEWAL_PERIOD)

        # Navigate to rate_limits array
        if KEY_AI_GATEWAY not in corrected_config:
            if rule_type == TYPE_REQUIRED:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} ({KEY_AI_GATEWAY} missing)"
                ))
                return

        if KEY_RATE_LIMITS not in corrected_config[KEY_AI_GATEWAY]:
            if rule_type == TYPE_REQUIRED:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} ({KEY_RATE_LIMITS} missing)"
                ))
                return
            elif rule_type == TYPE_FIXED:
                corrected_config[KEY_AI_GATEWAY][KEY_RATE_LIMITS] = []

        rate_limits = corrected_config[KEY_AI_GATEWAY][KEY_RATE_LIMITS]

        limit_entry, limit_index = self._find_rate_limit_entry(rate_limits, key_name, principal)

        if limit_entry is None:
            if rule_type == TYPE_REQUIRED:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' not found)"
                ))

            elif rule_type == TYPE_FIXED:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' missing)"
                ))
                # Always add new rate limit entry
                corrected_config[KEY_AI_GATEWAY][KEY_RATE_LIMITS].append(
                    self._set_rate_limit(key_name, default, renewal_period, principal)
                )
        else:
            current_value = limit_entry.get(KEY_CALLS)
            if current_value != default:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (expected: {default}, found: {current_value})",
                    expected=default,
                    found=current_value
                ))
                # Always update the calls value in the array
                corrected_config[KEY_AI_GATEWAY][KEY_RATE_LIMITS][limit_index][KEY_CALLS] = default

    def _apply_generic_rule(
        self,
        policy_key: str,
        rule_type: str,
        default: Any,
        error_message: str,
        corrected_config: Dict[str, Any],
        errors: List['ValidationError']
    ) -> None:
        """
        Internal method to apply a generic (non-rate_limit) rule to the configuration.

        Args:
            policy_key (str): The policy key
            rule_type (str): The type of rule ('required', 'fixed', etc.)
            default (Any): The default value to enforce
            error_message (str): Error message to use
            corrected_config (Dict[str, Any]): Config to correct
            errors (List[ValidationError]): List to append errors to
        """
        exists, value = self.search_nested_key(corrected_config, policy_key)

        if rule_type == TYPE_REQUIRED:
            if not exists:
                errors.append(ValidationError(
                    key=policy_key,
                    message=error_message
                ))

        elif rule_type == TYPE_FIXED:
            if not exists:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key missing)"
                ))
            elif value != default:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (expected: {default}, found: {value})",
                    expected=default,
                    found=value
                ))
