"""Data models for policy definitions."""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Literal


@dataclass
class PolicyRule:
    """Represents a single policy rule."""

    type: Literal["required", "fixed"]
    error_message: str
    default: Optional[Any] = None


@dataclass
class Policy:
    """Represents a complete policy definition."""

    name: str
    version: str
    rules: Dict[str, PolicyRule]
    description: Optional[str] = None
    applies_to: Optional[Dict[str, str]] = None
