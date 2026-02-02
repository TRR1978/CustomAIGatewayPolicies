"""Core policy engine for validating and applying policies to endpoint configurations."""

from typing import Dict, Tuple, Any, List
import logging

from src.custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Engine for validating and applying policies to endpoint configurations."""

    @staticmethod
    def parse_rate_limit_key(policy_key: str) -> Dict[str, Any]:
        """
        Parse a policy key into components for rate limit manipulation.

        Args:
            policy_key: Policy key in dot notation (e.g., 'ai_gateway.rate_limits.user.requests_per_minute')

        Returns:
            Dictionary with parsed components:
                - is_rate_limit: Whether this is a rate limit policy
                - key_name: The rate limit key name (e.g., 'user')
                - field: The field name (e.g., 'requests_per_minute')
                - renewal_period: The renewal period (e.g., 'minute')

        Examples:
            >>> PolicyEngine.parse_rate_limit_key('ai_gateway.rate_limits.user.requests_per_minute')
            {'is_rate_limit': True, 'key_name': 'user', 'field': 'requests_per_minute', 'renewal_period': 'minute'}
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
            data: Dictionary to search
            key: Key in dot notation (e.g., 'config.rate_limit')

        Returns:
            Tuple of (exists, value) where exists is True if key found

        Examples:
            >>> PolicyEngine.search_nested_key({'config': {'rate_limit': 100}}, 'config.rate_limit')
            (True, 100)
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
    ) -> PolicyResult:
        """
        Apply policy rules to an endpoint configuration.

        Always applies corrections. Use dry_mode at a higher level to control
        whether corrected_config is actually applied to the endpoint.

        Args:
            rules_policy: Dictionary of policy rules
            endpoint_config: Endpoint configuration to validate

        Returns:
            PolicyResult with validation results and corrected configuration

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
        errors: List[ValidationError]
    ) -> None:
        """Apply a single policy rule (internal method)."""
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

    def _apply_rate_limit_rule(
        self,
        policy_key: str,
        rule_type: str,
        default: Any,
        error_message: str,
        parsed: Dict[str, Any],
        corrected_config: Dict[str, Any],
        errors: List[ValidationError]
    ) -> None:
        """Apply a rate limit specific rule."""
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
                if rule_type == 'fixed':
                    corrected_config['ai_gateway']['rate_limits'] = []
            return

        rate_limits = corrected_config['ai_gateway']['rate_limits']

        # Check if it's just checking for rate_limits existence
        if policy_key == 'ai_gateway.rate_limits':
            if rule_type == 'required' and not rate_limits:
                errors.append(ValidationError(
                    key=policy_key,
                    message=error_message
                ))
            return

        # Find the specific rate limit entry by key
        limit_entry = None
        limit_index = None
        for idx, limit in enumerate(rate_limits):
            if limit.get('key') == key_name:
                limit_entry = limit
                limit_index = idx
                break

        if rule_type == 'required':
            if limit_entry is None:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' not found)"
                ))

        elif rule_type == 'fixed':
            if limit_entry is None:
                errors.append(ValidationError(
                    key=policy_key,
                    message=f"{error_message} (key '{key_name}' missing)"
                ))
                # Always add new rate limit entry
                corrected_config['ai_gateway']['rate_limits'].append({
                    'key': key_name,
                    'calls': default,
                    'renewal_period': renewal_period
                })
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
        errors: List[ValidationError]
    ) -> None:
        """Apply a generic (non-rate_limit) rule."""
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
