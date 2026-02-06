
"""
AI Gateway Policy Manager for Databricks.

This package provides tools and models for managing AI Gateway policies in Databricks environments.
"""
import os

from custom_ai_gateway_policies.manager import PolicyManager
from custom_ai_gateway_policies.domains.policy import Policy, PolicyRule
from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError


def get_version():
    version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'VERSION')
    with open(version_path, 'r') as f:
        return f.read().strip()


__version__ = get_version()

__all__ = [
    "PolicyManager",
    "Policy",
    "PolicyRule",
    "PolicyResult",
    "ValidationError",
]
