"""Policy loading utilities."""

import json
from typing import Dict, Any
from pathlib import Path
import logging

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
    required_fields = ["policy_name", "policy_version", "rules"]

    for field in required_fields:
        if field not in policy:
            raise ValueError(f"Policy missing required field: {field}")

    if not isinstance(policy["rules"], dict):
        raise ValueError("Policy 'rules' must be a dictionary")

    # Validate each rule
    for key, rule in policy["rules"].items():
        if "type" not in rule:
            raise ValueError(f"Rule '{key}' missing 'type' field")

        if rule["type"] not in ["required", "fixed"]:
            raise ValueError(f"Rule '{key}' has invalid type: {rule['type']}")

        if rule["type"] == "fixed" and "default" not in rule:
            raise ValueError(f"Rule '{key}' with type 'fixed' must have 'default' field")

    logger.info(f"Policy structure validated: {policy['policy_name']}")
    return True
