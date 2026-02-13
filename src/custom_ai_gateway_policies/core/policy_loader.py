"""Policy loading utilities."""

import json
from typing import Dict, Any
from pathlib import Path
import logging

from custom_ai_gateway_policies.constants import (
    REQUIRED_POLICY_FIELDS, RULES, POLICY_NAME,
    TYPE_VALUES, TYPE_FIXED, TYPE_REGEX,
    RULE_TYPE, RULE_DEFAULT, RULE_PATTERN
)

logger = logging.getLogger(__name__)


def read_policy(policy_path: str) -> Dict[str, Any]:
    """
    Read a policy from a JSON file.

    Args:
        policy_path (str): Path to the policy JSON file

    Returns:
        Dict[str, Any]: Dictionary containing the policy definition

    Raises:
        FileNotFoundError: If policy file doesn't exist
        json.JSONDecodeError: If policy file is not valid JSON

    Examples:
        >>> policy = read_policy("policy.json")
        >>> print(policy["policy_name"])
        'disabled-serving-policy'
    """
    logger.info(f"Reading policy from: {policy_path}")

    path = Path(policy_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            policy = json.load(f)

        logger.info(f"Successfully loaded policy: {policy.get('policy_name', 'unnamed')}")
        return policy
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in policy file {policy_path}: {e}")
        raise


def validate_policy_structure(policy: Dict[str, Any]) -> bool:
    """
    Validate that a policy has the required structure.

    Args:
        policy (Dict[str, Any]): Policy dictionary to validate

    Returns:
        bool: True if valid

    Raises:
        ValueError: If policy structure is invalid
    """
    for field in REQUIRED_POLICY_FIELDS:
        if field not in policy:
            raise ValueError(f"Policy missing required field: {field}")

    if not isinstance(policy[RULES], dict):
        raise ValueError(f"Policy '{RULES}' must be a dictionary")

    # Validate each rule
    for key, rule in policy[RULES].items():
        if RULE_TYPE not in rule:
            raise ValueError(f"Rule '{key}' missing '{RULE_TYPE}' field")

        if rule[RULE_TYPE] not in TYPE_VALUES:
            raise ValueError(f"Rule '{key}' has invalid type: {rule[RULE_TYPE]}")

        if rule[RULE_TYPE] == TYPE_FIXED and RULE_DEFAULT not in rule:
            raise ValueError(f"Rule '{key}' with type '{TYPE_FIXED}' must have '{RULE_DEFAULT}' field")

        if rule[RULE_TYPE] == TYPE_REGEX and RULE_PATTERN not in rule:
            raise ValueError(f"Rule '{key}' with type '{TYPE_REGEX}' must have '{RULE_PATTERN}' field")

    logger.info(f"Policy structure validated: {policy[POLICY_NAME]}")
    return True


def check_policy_duplicate(policies: Dict[str, Dict[str, Any]]) -> bool:
    """
    Check if a policy with the same name

    Args:
        policies (Dict[str, Dict[str, Any]]): Dictionary of existing policies keyed by "name:version"

    Returns:
        bool: True if duplicate exists
    """
    seen = set()
    policy_names = [p.get(POLICY_NAME) for p in policies]
    for key in policy_names:
        if key in seen:
            return True
        seen.add(key)
    return False
