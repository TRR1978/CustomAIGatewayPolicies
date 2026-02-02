"""Main PolicyManager class - high-level API for policy management."""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

from src.custom_ai_gateway_policies.adapters.databricks_adapter import DatabricksEndpointAdapter
from src.custom_ai_gateway_policies.core.policy_engine import PolicyEngine
from src.custom_ai_gateway_policies.core.policy_loader import read_policy, validate_policy_structure
from src.custom_ai_gateway_policies.core.filters import apply_to_filter, matches_filter
from src.custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError

logger = logging.getLogger(__name__)


class PolicyManager:
    """
    High-level API for managing and applying policies to Databricks serving endpoints.

    Examples:
        >>> manager = PolicyManager()
        >>> policy = manager.load_policy("policy.json")
        >>> result = manager.apply_policy("my-endpoint", policy, dry_mode=True)
        >>> if not result.is_compliant:
        ...     print(f"Found {len(result.errors)} violations")
    """

    def __init__(self, adapter: Optional[DatabricksEndpointAdapter] = None):
        """
        Initialize the PolicyManager.

        Args:
            adapter: Optional DatabricksEndpointAdapter instance. If not provided,
                    creates a new one with default authentication.
        """
        self.adapter = adapter or DatabricksEndpointAdapter()
        self.engine = PolicyEngine()
        logger.info("PolicyManager initialized")

    def load_policy(self, policy_source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Load a policy from a file or dictionary.

        Args:
            policy_source: Path to JSON file or policy dictionary

        Returns:
            Policy dictionary

        Raises:
            ValueError: If policy structure is invalid
            FileNotFoundError: If policy file doesn't exist

        Examples:
            >>> manager = PolicyManager()
            >>> policy = manager.load_policy("policy.json")
            >>> policy = manager.load_policy({"policy_name": "test", ...})
        """
        if isinstance(policy_source, dict):
            policy = policy_source
            logger.info(f"Using policy dictionary: {policy.get('policy_name', 'unnamed')}")
        else:
            policy = read_policy(str(policy_source))

        # Validate structure
        validate_policy_structure(policy)

        return policy

    def apply_policy(
        self,
        endpoint_name: str,
        policy: Dict[str, Any],
        dry_mode: bool = True
    ) -> PolicyResult:
        """
        Apply a policy to a single endpoint.

        Args:
            endpoint_name: Name of the endpoint
            policy: Policy dictionary (from load_policy)
            dry_mode: If True, only validate and return corrections without applying.
                     If False, apply corrections to the actual endpoint.

        Returns:
            PolicyResult with validation results and corrected configuration

        Examples:
            >>> manager = PolicyManager()
            >>> policy = manager.load_policy("policy.json")
            >>> result = manager.apply_policy("my-endpoint", policy, dry_mode=True)
            >>> if not result.is_compliant:
            ...     print("Endpoint does not comply with policy")
        """
        logger.info(f"Applying policy to endpoint: {endpoint_name} (dry_mode={dry_mode})")

        # Get current endpoint configuration
        try:
            endpoint_config = self.adapter.get_serving_endpoint_details(endpoint_name)
        except Exception as e:
            logger.error(f"Failed to get endpoint {endpoint_name}: {e}")
            return PolicyResult(
                is_compliant=False,
                corrected_config={},
                errors=[ValidationError(
                    key="endpoint",
                    message=f"Failed to retrieve endpoint: {str(e)}"
                )],
                endpoint_name=endpoint_name
            )

        # Check if policy applies to this endpoint
        applies_to = policy.get("applies_to", {})
        if applies_to and not matches_filter(endpoint_config, applies_to):
            logger.info(f"Policy does not apply to endpoint {endpoint_name}")
            return PolicyResult(
                is_compliant=True,
                corrected_config=endpoint_config,
                errors=[],
                endpoint_name=endpoint_name
            )

        # Apply policy rules
        rules = policy.get("rules", {})
        result = self.engine.apply_policy(rules, endpoint_config)
        result.endpoint_name = endpoint_name

        # Apply corrections if not in dry mode
        if not dry_mode and not result.is_compliant:
            logger.info(f"Applying corrections to endpoint {endpoint_name}")
            try:
                self.adapter.update_ai_gateway(endpoint_name, result.corrected_config)
                logger.info(f"Successfully updated endpoint {endpoint_name}")
            except Exception as e:
                logger.error(f"Failed to update endpoint {endpoint_name}: {e}")
                result.errors.append(ValidationError(
                    key="update",
                    message=f"Failed to apply corrections: {str(e)}"
                ))

        return result

    def apply_policy_bulk(
        self,
        policy: Dict[str, Any],
        filter_dict: Optional[Dict[str, str]] = None,
        dry_mode: bool = True
    ) -> List[PolicyResult]:
        """
        Apply a policy to multiple endpoints matching a filter.

        Args:
            policy: Policy dictionary (from load_policy)
            filter_dict: Optional filter criteria (e.g., {"name": "^databricks-.*"}).
                        If None, uses policy's "applies_to" field.
            dry_mode: If True, only validate without applying corrections

        Returns:
            List of PolicyResult objects, one per endpoint

        Examples:
            >>> manager = PolicyManager()
            >>> policy = manager.load_policy("policy.json")
            >>> results = manager.apply_policy_bulk(
            ...     policy,
            ...     filter_dict={"name": "^databricks-.*"},
            ...     dry_mode=True
            ... )
            >>> compliant = sum(1 for r in results if r.is_compliant)
            >>> print(f"{compliant}/{len(results)} endpoints compliant")
        """
        # Determine filter
        if filter_dict is None:
            filter_dict = policy.get("applies_to", {})

        logger.info(f"Applying policy to multiple endpoints (filter={filter_dict}, dry_mode={dry_mode})")

        # Get all endpoints
        all_endpoints_df = self.adapter.list_endpoints()

        # Apply filter
        if filter_dict:
            filtered_df = apply_to_filter(all_endpoints_df, filter_dict)
        else:
            filtered_df = all_endpoints_df

        logger.info(f"Found {len(filtered_df)} endpoints matching filter")

        # Apply policy to each endpoint
        results = []
        for _, endpoint_row in filtered_df.iterrows():
            endpoint_name = endpoint_row["name"]
            result = self.apply_policy(endpoint_name, policy, dry_mode=dry_mode)
            results.append(result)

        # Summary
        compliant_count = sum(1 for r in results if r.is_compliant)
        logger.info(f"Policy application complete: {compliant_count}/{len(results)} compliant")

        return results

    def get_compliance_report(
        self,
        results: List[PolicyResult]
    ) -> Dict[str, Any]:
        """
        Generate a compliance report from policy results.

        Args:
            results: List of PolicyResult objects

        Returns:
            Dictionary with compliance statistics

        Examples:
            >>> results = manager.apply_policy_bulk(policy, dry_mode=True)
            >>> report = manager.get_compliance_report(results)
            >>> print(f"Compliance rate: {report['compliance_rate']:.1%}")
        """
        total = len(results)
        compliant = sum(1 for r in results if r.is_compliant)
        non_compliant = total - compliant

        # Collect all errors
        all_errors = []
        for result in results:
            for error in result.errors:
                all_errors.append({
                    "endpoint": result.endpoint_name,
                    "key": error.key,
                    "message": error.message
                })

        report = {
            "total_endpoints": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "compliance_rate": compliant / total if total > 0 else 0,
            "total_violations": len(all_errors),
            "violations": all_errors
        }

        logger.info(f"Generated compliance report: {compliant}/{total} compliant")
        return report
