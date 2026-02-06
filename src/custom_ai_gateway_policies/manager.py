"""Main PolicyManager class - high-level API for policy management."""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

from custom_ai_gateway_policies.adapters.databricks_adapter import DatabricksEndpointAdapter
from custom_ai_gateway_policies.core.policy_engine import PolicyEngine
from custom_ai_gateway_policies.core.policy_loader import read_policy, validate_policy_structure, check_policy_duplicate
from custom_ai_gateway_policies.core.filters import apply_to_filter, matches_filter
from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError

from custom_ai_gateway_policies.constants import RULES, APPLIES_TO, POLICY_NAME

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

        # Apply policy to multiple endpoints
        >>> bulk_results = manager.apply_policy_bulk(policy, filter_dict={"name": "^databricks-.*"}, dry_mode=True)
        >>> for res in bulk_results:
        ...     print(f"Endpoint: {res.endpoint_name}, Compliant: {res.is_compliant}")
    """

    def __init__(self, adapter: Optional[DatabricksEndpointAdapter] = None) -> None:
        """
        Initialize the PolicyManager.

        Args:
            adapter (Optional[DatabricksEndpointAdapter]): Optional DatabricksEndpointAdapter instance.
            If not provided, creates a new one with default authentication.

        Returns:
            None
        """
        self.adapter = adapter or DatabricksEndpointAdapter()
        self.engine = PolicyEngine()
        logger.info("PolicyManager initialized")

    def load_policy(self, policy_source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Load a policy from a file or dictionary.

        Args:
            policy_source (Union[str, Path, Dict[str, Any]]): Path to JSON file or policy dictionary

        Returns:
            Dict[str, Any]: Policy dictionary

        Raises:
            ValueError: If policy structure is invalid
            FileNotFoundError: If policy file doesn't exist
        """
        if isinstance(policy_source, dict):
            policy = policy_source
            logger.info(f"Using policy dictionary: {policy.get('policy_name', 'unnamed')}")
        else:
            policy = read_policy(str(policy_source))

        # Validate structure
        validate_policy_structure(policy)

        return policy

    def load_policies_bulk(self, policy_source_path: Path) -> List[Dict[str, Any]]:
        """
        Load multiple policies from a directory containing JSON policy files.

        Args:
            policy_source_path (Path): Path to the directory containing policy JSON files.

        Returns:
            List[Dict[str, Any]]: List of loaded policy dictionaries.

        Raises:
            FileNotFoundError: If the provided path does not exist or is not a directory.

        Notes:
            - Only files with a .json extension are loaded.
            - Invalid or unreadable policy files are skipped with an error logged.
        """
        policies = []
        # Convert to Path if a string is provided
        if isinstance(policy_source_path, str):
            policy_source_path = Path(policy_source_path)

        # check if path exists and is a directory
        if not policy_source_path.exists() or not policy_source_path.is_dir():
            logger.error(f"Policy source path is invalid: {policy_source_path}")
            raise FileNotFoundError(f"Policy source path not found or not a directory: {policy_source_path}")

        for policy_file in policy_source_path.glob("*.json"):
            try:
                policy = self.load_policy(policy_file)
                policies.append(policy)
            except Exception as e:
                logger.error(f"Failed to load policy from {policy_file}: {e}")

        if check_policy_duplicate(policies):
            logger.error("Duplicate policy names found in the loaded policies")
            raise ValueError("Duplicate policy names detected. Ensure all policies have unique 'policy_name' fields.")

        return policies

    def apply_policy(
        self,
        endpoint_name: str,
        policy: Dict[str, Any],
        dry_mode: bool = True
    ) -> PolicyResult:
        """
        Apply a policy to a single endpoint.

        Args:
            endpoint_name (str): Name of the endpoint
            policy (Dict[str, Any]): Policy dictionary (from load_policy)
            dry_mode (bool): If True, only validate and return corrections without applying.
            If False, apply corrections to the actual endpoint.

        Returns:
            PolicyResult: Validation results and corrected configuration
        """
        logger.info(f"Applying policy to endpoint: {endpoint_name} (dry_mode={dry_mode})")

        policy_name = policy.get(POLICY_NAME)
        # Check if policy applies to this endpoint
        applies_to = policy.get(APPLIES_TO, {})

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
                endpoint_name=endpoint_name,
                policy_name=policy_name
            )

        if applies_to and not matches_filter(endpoint_config, applies_to):
            logger.info(f"Policy does not apply to endpoint {endpoint_name}")
            return PolicyResult(
                is_compliant=True,
                corrected_config=endpoint_config,
                errors=[],
                endpoint_name=endpoint_name,
                policy_name=policy_name
            )

        # Apply policy rules
        rules = policy.get(RULES, {})
        result = self.engine.apply_policy(policy_name, rules, endpoint_config)
        result.endpoint_name = endpoint_name

        # Apply corrections if not in dry mode
        if not dry_mode and not result.is_compliant:
            logger.info(f"Applying corrections to endpoint {endpoint_name}")
            try:
                self.adapter.update_ai_gateway(endpoint_name, result.corrected_config)
                logger.info(f"Successfully updated endpoint {endpoint_name}")
                # if update is successful, re-apply policy to confirm compliance
                result = self.engine.apply_policy(policy_name, rules, endpoint_config)
                logger.info(f"Re-validation after update: is_compliant={result.is_compliant}")

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
            policy (Dict[str, Any]): Policy dictionary (from load_policy)
            filter_dict (Optional[Dict[str, str]]): Optional filter criteria (e.g., {"name": "^databricks-.*"}).
            If None, uses policy's "applies_to" field.
            dry_mode (bool): If True, only validate without applying corrections

        Returns:
            List[PolicyResult]: List of PolicyResult objects, one per endpoint
        """
        # Determine filter
        if filter_dict is None:
            filter_dict = policy.get(APPLIES_TO, {})

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

    def apply_policies_bulk(
        self,
        policies: List[Dict[str, Any]],
        filter_dict: Optional[Dict[str, str]] = None,
        dry_mode: bool = True
    ) -> List[PolicyResult]:
        """
        Apply multiple policies to endpoints matching a filter.

        Args:
            policies (List[Dict[str, Any]]): List of policy dictionaries.
            filter_dict (Optional[Dict[str, str]]): Optional filter criteria for selecting endpoints.
            dry_mode (bool): If True, only validate without applying corrections.

        Returns:
            Dict[str, List[PolicyResult]]: Dictionary mapping policy names to lists of PolicyResult objects.
        """
        results = []
        for policy in policies:
            policy_name = policy.get("policy_name", "unnamed")
            logger.info(f"Applying policy: {policy_name}")
            results_policy = self.apply_policy_bulk(policy,
                                                    filter_dict=filter_dict,
                                                    dry_mode=dry_mode)
            results.extend(results_policy)

        return results

    def get_compliance_report(
        self,
        results: List[PolicyResult]
    ) -> Dict[str, Any]:
        """
        Generate a compliance report from policy results.

        Args:
            results (List[PolicyResult]): List of PolicyResult objects

        Returns:
            Dict[str, Any]: Dictionary with compliance statistics
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
