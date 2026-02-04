"""Data models for policy definitions."""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Literal


@dataclass
class PolicyRule:
    """
    Represents a single policy rule.

    Attributes:
        type (Literal["required", "fixed"]): The type of rule.
        error_message (str): The error message to display if the rule is violated.
        default (Optional[Any]): The default value for 'fixed' rules.
    """
    type: Literal["required", "fixed"]
    error_message: str
    default: Optional[Any] = None


@dataclass
class Policy:
    """
    Represents a complete policy definition.

    Attributes:
        name (str): The name of the policy.
        version (str): The version of the policy.
        rules (Dict[str, PolicyRule]): The rules in the policy.
        description (Optional[str]): Optional description of the policy.
        applies_to (Optional[Dict[str, str]]): Optional filter for endpoints to which the policy applies.
    """
    name: str
    version: str
    rules: Dict[str, PolicyRule]
    description: Optional[str] = None
    applies_to: Optional[Dict[str, str]] = None
