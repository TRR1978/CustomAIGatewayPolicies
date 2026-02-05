"""Core policy engine for validating and applying policies to endpoint configurations."""

from typing import Dict, Tuple, Any, List
import logging

from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Engine for validating and applying policies to endpoint configurations."""

    @staticmethod
    def parse_rate_limit_key(policy_key: str) -> Dict[str, Any]:
        """
        Parse a policy key into components for rate limit manipulation.

        Args:
            policy_key (str): Policy key in dot notation (e.g., 'ai_gateway.rate_limits.user.requests_per_minute')

        Returns:
            Dict[str, Any]: Dictionary with parsed components:
                - is_rate_limit: Whether this is a rate limit policy
                - key_name: The rate limit key name (e.g., 'user')
                - field: The field name (e.g., 'requests_per_minute')
                - renewal_period: The renewal period (e.g., 'minute')
        """
        parts = policy_key.split('.')

        if len(parts) >= 4 and parts[0] == 'ai_gateway' and parts[1] == 'rate_limits':
            key_name = parts[2]
            field = parts[3]
            renewal_period = field.replace('requests_per_', '') if field.startswith('requests_per_') else 'minute'

            return {
                'is_rate_limit': True,
                'key_name': key_name,
                'field': field,
                'renewal_period': renewal_period
            }

        return {'is_rate_limit': False}

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
        rules_policy: Dict[str, Dict[str, Any]],
        endpoint_config: Dict[str, Any]
    ) -> 'PolicyResult':
        """
        Apply policy rules to an endpoint configuration.

        Always applies corrections. Use dry_mode at a higher level to control
        whether corrected_config is actually applied to the endpoint.

        Args:
            rules_policy (Dict[str, Dict[str, Any]]): Dictionary of policy rules
            endpoint_config (Dict[str, Any]): Endpoint configuration to validate

        Returns:
            PolicyResult: Validation results and corrected configuration

        Raises:
            ValueError: If rules_policy or endpoint_config is invalid
        """
        if not isinstance(rules_policy, dict):
            raise ValueError("rules_policy must be a dictionary")
        if not isinstance(endpoint_config, dict):
            raise ValueError("endpoint_config must be a dictionary")

        errors: List[ValidationError] = []
        corrected_config = endpoint_config.copy()

        logger.info(f"Applying {len(rules_policy)} policy rules")

        for policy_key, rule in rules_policy.items():
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
            errors=errors
        )

    def _apply_single_rule(
        self,
        policy_key: str,
        rule: Dict[str, Any],
        corrected_config: Dict[str, Any],
        errors: List['ValidationError']
    ) -> None:
        """
        Apply a single policy rule (internal method).

        Args:
            policy_key (str): The policy key to apply
            rule (Dict[str, Any]): The rule definition
            corrected_config (Dict[str, Any]): The config to correct
            errors (List[ValidationError]): List to append errors to

        Returns:
            None
        """
        rule_type = rule.get("type")
        default = rule.get("default")
        error_message = rule.get("error_message", f"Policy violation for {policy_key}")

        parsed = self.parse_rate_limit_key(policy_key)

        if parsed['is_rate_limit']:
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

    def _find_rate_limit_entry(self, rate_limits, key_name):
        # Find the specific rate limit entry by key
        limit_entry = None
        limit_index = None
        for idx, limit in enumerate(rate_limits):
            if ((limit.get('key') == key_name) or 
                (limit.get('key') == 'user_group' and limit.get('principal') == key_name)):
                limit_entry = limit
                limit_index = idx
                break
        return limit_entry, limit_index
    
    def _set_rate_limit(self, key_name, default, renewal_period):
        rate_limit = {}
        if key_name in ('user'):
            rate_limit['key'] = key_name
            rate_limit['calls'] = default
            rate_limit['renewal_period'] = renewal_period
        else:
            rate_limit['key'] = 'user_group'
            rate_limit['principal'] = key_name
            rate_limit['calls'] = default
            rate_limit['renewal_period'] = renewal_period
            
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
        Apply a rate limit specific rule.

        Args:
            policy_key (str): The policy key
            rule_type (str): The type of rule ('required', 'fixed', etc.)
            default (Any): The default value to enforce
            error_message (str): Error message to use
            parsed (Dict[str, Any]): Parsed key info
            corrected_config (Dict[str, Any]): Config to correct
            errors (List[ValidationError]): List to append errors to

        Returns:
            None
        """
        key_name = parsed['key_name']
        renewal_period = parsed['renewal_period']

        # Navigate to rate_limits array
        if 'ai_gateway' not in corrected_config:
            if rule_type == 'required':
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (ai_gateway missing)"
                ))
                return

        if 'rate_limits' not in corrected_config['ai_gateway']:
            if rule_type == 'required':
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (rate_limits missing)"
                ))
                return
            elif rule_type == 'fixed':
                corrected_config['ai_gateway']['rate_limits'] = []

        rate_limits = corrected_config['ai_gateway']['rate_limits']

        limit_entry, limit_index = self._find_rate_limit_entry(rate_limits, key_name)

        if limit_entry is None:
            if rule_type == 'required':
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' not found)"
                ))

            elif rule_type == 'fixed':
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' missing)"
                ))
                # Always add new rate limit entry
                corrected_config['ai_gateway']['rate_limits'].append(self._set_rate_limit(key_name, default, renewal_period))
                 
        else:
            current_value = limit_entry.get('calls')
            if current_value != default:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (expected: {default}, found: {current_value})",
                    expected=default,
                    found=current_value
                ))
                # Always update the calls value in the array
                corrected_config['ai_gateway']['rate_limits'][limit_index]['calls'] = default

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
        Apply a generic (non-rate_limit) rule.

        Args:
            policy_key (str): The policy key
            rule_type (str): The type of rule ('required', 'fixed', etc.)
            default (Any): The default value to enforce
            error_message (str): Error message to use
            corrected_config (Dict[str, Any]): Config to correct
            errors (List[ValidationError]): List to append errors to

        Returns:
            None
        """
        exists, value = self.search_nested_key(corrected_config, policy_key)

        if rule_type == 'required':
            if not exists:
                errors.append(ValidationError(
                    key=policy_key,
                    message=error_message
                ))

        elif rule_type == 'fixed':
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
