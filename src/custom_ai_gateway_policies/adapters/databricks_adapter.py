"""Adapter for Databricks Serving Endpoints API."""

import logging
import pandas as pd

from typing import Dict, Any, List
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    AiGatewayRateLimit,
    AiGatewayRateLimitRenewalPeriod,
    AiGatewayRateLimitKey,
    FallbackConfig,
    AiGatewayUsageTrackingConfig
)
from custom_ai_gateway_policies.constants import (
    KEY_AI_GATEWAY, KEY_RATE_LIMITS, KEY_FALLBACK_CONFIG, KEY_CALLS, KEY_PRINCIPAL, KEY_KEY,
    KEY_RENEWAL_PERIOD, MINUTE, TOKENS, NAME, RECORDS, ENABLED, KEY_USAGE_TRACKING_CONFIG
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

    def _set_rate_limits(self, rate_limit_array: List[Dict[str, Any]]) -> List[AiGatewayRateLimit]:
        """
        Convert a list of rate limit dictionaries to a list of AiGatewayRateLimit objects.

        Args:
            rate_limit_array (List[Dict[str, Any]]): List of rate limit configurations as dictionaries

        Returns:
            List[AiGatewayRateLimit]: List of AiGatewayRateLimit objects
        """
        rate_limit_objects = []
        for rl in rate_limit_array:
            # Map renewal_period string to enum
            renewal_period_str = rl.get(KEY_RENEWAL_PERIOD, MINUTE).upper()
            renewal_period = getattr(
                AiGatewayRateLimitRenewalPeriod,
                renewal_period_str,
                AiGatewayRateLimitRenewalPeriod.MINUTE
            )

            # Map key string to enum
            key_str = rl.get(NAME, "user").upper()
            key_enum = getattr(
                AiGatewayRateLimitKey,
                key_str,
                AiGatewayRateLimitKey.USER
            )

            # Create rate limit object
            rate_limit_kwargs = {
                KEY_RENEWAL_PERIOD: renewal_period,
                KEY_KEY: key_enum
            }
            if KEY_PRINCIPAL in rl:
                rate_limit_kwargs[KEY_PRINCIPAL] = rl[KEY_PRINCIPAL]
            if KEY_CALLS in rl:
                rate_limit_kwargs[KEY_CALLS] = rl[KEY_CALLS]
            if TOKENS in rl:
                rate_limit_kwargs[TOKENS] = rl[TOKENS]

            rate_limit_objects.append(AiGatewayRateLimit(**rate_limit_kwargs))

        return rate_limit_objects

    def _set_fallback_config(self, fallback_config: Dict[str, Any]) -> FallbackConfig:
        """
        Convert fallback configuration dictionary to a FallbackConfig object.

        Args:
            fallback_config (Dict[str, Any]): Fallback configuration as dictionary

        Returns:
            FallbackConfig: Fallback configuration object
        """
        if not isinstance(fallback_config.get(ENABLED), bool):
            raise ValueError("Fallback config must have 'enabled' set to True or False")

        return FallbackConfig(
            enabled=fallback_config.get(ENABLED)
        )

    def _set_usage_tracking_config(self, usage_tracking_config: Dict[str, Any]) -> AiGatewayUsageTrackingConfig:
        """
        Convert usage tracking configuration dictionary to a UsageTrackingConfig object.

        Args:
            usage_tracking_config (Dict[str, Any]): Usage tracking configuration as dictionary

        Returns:
            UsageTrackingConfig: Usage tracking configuration object
        """
        if not isinstance(usage_tracking_config.get(ENABLED), bool):
            raise ValueError("Usage tracking config must have 'enabled' set to True or False")

        return AiGatewayUsageTrackingConfig(
            enabled=usage_tracking_config.get(ENABLED)
        )

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
            # Extract AI Gateway config sections
            ai_gateway_config = corrected_config.get(KEY_AI_GATEWAY, {})
            rate_limits_array = ai_gateway_config.get(KEY_RATE_LIMITS, [])
            fallback_config = ai_gateway_config.get(KEY_FALLBACK_CONFIG)
            usage_config = ai_gateway_config.get(KEY_USAGE_TRACKING_CONFIG)

            has_configuration = False
            if rate_limits_array:
                rate_limit_objects = self._set_rate_limits(rate_limits_array)
                has_configuration = True
            else:
                rate_limit_objects = None

            if fallback_config:
                fallback_object = self._set_fallback_config(fallback_config)
                has_configuration = True
            else:
                fallback_object = None

            if usage_config:
                usage_tracking_object = self._set_usage_tracking_config(usage_config)
                has_configuration = True
            else:
                usage_tracking_object = None

            if has_configuration:
                self.w.serving_endpoints.put_ai_gateway(
                    name=endpoint_name,
                    rate_limits=rate_limit_objects,
                    fallback_config=fallback_object,
                    usage_tracking_config=usage_tracking_object
                )
                logger.info(f"Successfully updated AI Gateway for {endpoint_name}")
            else:
                logger.info(f"No changes detected for AI Gateway of {endpoint_name}")

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
        if NAME in filter_dict:
            pattern = filter_dict[NAME]
            filtered = all_endpoints[all_endpoints[NAME].str.match(pattern)]
            logger.info(f"Filter matched {len(filtered)} endpoints")
            return filtered.to_dict(RECORDS)

        return all_endpoints.to_dict(RECORDS)
