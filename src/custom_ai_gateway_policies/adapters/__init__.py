
"""
Adapters for external services.

This subpackage provides adapters for integrating with external APIs and services (e.g., Databricks).
"""

from custom_ai_gateway_policies.adapters.databricks_adapter import DatabricksEndpointAdapter

__all__ = ["DatabricksEndpointAdapter"]
