"""Adapter for Databricks Serving Endpoints API."""
import logging
import pandas as pd

from typing import Dict, Any, List
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    AiGatewayRateLimit,
    AiGatewayRateLimitRenewalPeriod,
    AiGatewayRateLimitKey
)


logger = logging.getLogger(__name__)


class DatabricksEndpointAdapter:
    """Adapter for interacting with Databricks Model Serving endpoints."""

    def __init__(self, workspace_client: WorkspaceClient = None) -> None:
        """
        Initialize the adapter.

        Args:
            workspace_client (WorkspaceClient, optional): Optional WorkspaceClient instance. If not provided,
            will create one using default authentication.

        Returns:
            None
        """
        self.w = workspace_client or WorkspaceClient()
        logger.info("DatabricksEndpointAdapter initialized")

    def list_endpoints(self) -> pd.DataFrame:
        """
        List all serving endpoints in the workspace.

        Returns:
            pd.DataFrame: DataFrame with endpoint information
        """
        logger.info("Listing all serving endpoints")
        endpoints = self.w.serving_endpoints.list()
        endpoints_list = [endpoint.as_dict() for endpoint in endpoints]

        df = pd.DataFrame(endpoints_list)
        logger.info(f"Found {len(df)} endpoints")
        return df

    def get_serving_endpoint_details(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific serving endpoint.

        Args:
            endpoint_name (str): Name of the endpoint

        Returns:
            Dict[str, Any]: Dictionary with endpoint configuration

        Raises:
            Exception: If endpoint not found or API call fails
        """
        logger.info(f"Getting details for endpoint: {endpoint_name}")
        try:
            endpoint = self.w.serving_endpoints.get(name=endpoint_name)
            endpoint_dict = endpoint.as_dict()
            logger.debug(f"Retrieved endpoint details for {endpoint_name}")
            return endpoint_dict
        except Exception as e:
            logger.error(f"Failed to get endpoint {endpoint_name}: {e}")
            raise

    def update_ai_gateway(
        self,
        endpoint_name: str,
        corrected_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update AI Gateway configuration (rate limits) for an endpoint. Compatible with Databricks foundation models.

        Args:
            endpoint_name (str): Name of the endpoint to update
            corrected_config (Dict[str, Any]): Configuration dictionary with corrected rate_limits

        Returns:
            Dict[str, Any]: Updated endpoint configuration dictionary

        Raises:
            Exception: If update fails
        """
        logger.info(f"Updating AI Gateway for endpoint: {endpoint_name}")
        try:
            # Extract rate_limits from corrected config
            rate_limits_array = corrected_config.get("ai_gateway", {}).get("rate_limits", [])

            if not rate_limits_array:
                raise ValueError(f"No rate_limits found in corrected_config for {endpoint_name}")

            # Convert to SDK objects with proper enums
            rate_limit_objects = []
            for rl in rate_limits_array:
                # Map renewal_period string to enum
                renewal_period_str = rl.get("renewal_period", "minute").upper()
                renewal_period = getattr(
                    AiGatewayRateLimitRenewalPeriod,
                    renewal_period_str,
                    AiGatewayRateLimitRenewalPeriod.MINUTE
                )

                # Map key string to enum
                key_str = rl.get("key", "user").upper()
                key_enum = getattr(
                    AiGatewayRateLimitKey,
                    key_str,
                    AiGatewayRateLimitKey.USER
                )

                # Create rate limit object
                # Support both 'calls' and 'tokens' limits
                rate_limit_kwargs = {
                    "renewal_period": renewal_period,
                    "key": key_enum
                }
                
                if "principal" in rl:
                    rate_limit_kwargs["principal"] = rl["principal"]

                if "calls" in rl:
                    rate_limit_kwargs["calls"] = rl["calls"]
                if "tokens" in rl:
                    rate_limit_kwargs["tokens"] = rl["tokens"]

                rate_limit_objects.append(AiGatewayRateLimit(**rate_limit_kwargs))

            # Update AI Gateway using put_ai_gateway
            self.w.serving_endpoints.put_ai_gateway(
                name=endpoint_name,
                rate_limits=rate_limit_objects
            )

            logger.info(f"Successfully updated AI Gateway for {endpoint_name}")

            # Return updated configuration
            return self.get_serving_endpoint_details(endpoint_name)

        except Exception as e:
            logger.error(f"Failed to update AI Gateway for {endpoint_name}: {e}")
            raise

    def get_endpoints_by_filter(self, filter_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get endpoints matching a filter.

        Args:
            filter_dict (Dict[str, str]): Dictionary with filter criteria (e.g., {"name": "^databricks-.*"})

        Returns:
            List[Dict[str, Any]]: List of endpoint dictionaries matching the filter
        """
        logger.info(f"Filtering endpoints with: {filter_dict}")
        all_endpoints = self.list_endpoints()

        # Apply filters (currently only supports name regex)
        if "name" in filter_dict:
            pattern = filter_dict["name"]
            filtered = all_endpoints[all_endpoints["name"].str.match(pattern)]
            logger.info(f"Filter matched {len(filtered)} endpoints")
            return filtered.to_dict('records')

        return all_endpoints.to_dict('records')
