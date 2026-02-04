"""Data models for policy validation results."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ValidationError:
    """
    Represents a policy validation error.

    Attributes:
        key (str): The key of the policy or config that failed validation.
        message (str): The error message.
        expected (Optional[Any]): The expected value, if applicable.
        found (Optional[Any]): The found value, if applicable.
    """
    key: str
    message: str
    expected: Optional[Any] = None
    found: Optional[Any] = None

    @property
    def error(self) -> str:
        """
        Alias for message to maintain backward compatibility.

        Returns:
            str: The error message.
        """
        return self.message


@dataclass
class PolicyResult:
    """
    Result of applying a policy to an endpoint configuration.

    Attributes:
        is_compliant (bool): Whether the endpoint is compliant with the policy.
        corrected_config (Dict[str, Any]): The corrected configuration.
        errors (List[ValidationError]): List of validation errors.
        endpoint_name (Optional[str]): Name of the endpoint.
    """
    is_compliant: bool
    corrected_config: Dict[str, Any]
    errors: List[ValidationError]
    endpoint_name: Optional[str] = None

    def __bool__(self) -> bool:
        """
        Allow using result in boolean context.

        Returns:
            bool: True if compliant, False otherwise.
        """
        return self.is_compliant
