"""Data models for policy validation results."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ValidationError:
    """Represents a policy validation error."""

    key: str
    message: str
    expected: Optional[Any] = None
    found: Optional[Any] = None

    @property
    def error(self) -> str:
        """Alias for message to maintain backward compatibility."""
        return self.message


@dataclass
class PolicyResult:
    """Result of applying a policy to an endpoint configuration."""

    is_compliant: bool
    corrected_config: Dict[str, Any]
    errors: List[ValidationError]
    endpoint_name: Optional[str] = None

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.is_compliant
