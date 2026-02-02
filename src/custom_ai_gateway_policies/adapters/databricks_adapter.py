"""Adapter for Databricks Serving Endpoints API."""
import logging
import pandas as pd

from typing import Dict, Any, List
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServingEndpointDetailed


logger = logging.getLogger(__name__)


class DatabricksEndpointAdapter:
    """Adapter for interacting with Databricks Model Serving endpoints."""

    def __init__(self, workspace_client: WorkspaceClient = None):
        """
        Initialize the adapter.

        Args:
            workspace_client: Optional WorkspaceClient instance. If not provided,
                            will create one using default authentication.
        """
        self.w = workspace_client or WorkspaceClient()
        logger.info("DatabricksEndpointAdapter initialized")

    def list_endpoints(self) -> pd.DataFrame:
        """
        List all serving endpoints in the workspace.

        Returns:
            DataFrame with endpoint information
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
            endpoint_name: Name of the endpoint

        Returns:
            Dictionary with endpoint configuration

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

    def update_endpoint(
        self,
        endpoint_name: str,
        config: Dict[str, Any]
    ) -> ServingEndpointDetailed:
        """
        Update an endpoint configuration.

        Args:
            endpoint_name: Name of the endpoint to update
            config: New configuration dictionary

        Returns:
            Updated endpoint details

        Raises:
            Exception: If update fails
        """
        logger.info(f"Updating endpoint: {endpoint_name}")
        try:
            # Convert dict to ServingEndpointDetailed object
            endpoint_detailed = ServingEndpointDetailed.from_dict(config)

            # Update the endpoint
            updated = self.w.serving_endpoints.update_config(
                name=endpoint_name,
                served_entities=endpoint_detailed.config.served_entities,
                traffic_config=endpoint_detailed.config.traffic_config,
                auto_capture_config=endpoint_detailed.config.auto_capture_config,
            )

            logger.info(f"Successfully updated endpoint {endpoint_name}")
            return updated
        except Exception as e:
            logger.error(f"Failed to update endpoint {endpoint_name}: {e}")
            raise

    def get_endpoints_by_filter(self, filter_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get endpoints matching a filter.

        Args:
            filter_dict: Dictionary with filter criteria (e.g., {"name": "^databricks-.*"})

        Returns:
            List of endpoint dictionaries matching the filter
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
