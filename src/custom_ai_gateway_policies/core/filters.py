"""Filtering utilities for endpoints."""

import re
from typing import Dict, Any
import pandas as pd
import logging
from custom_ai_gateway_policies.constants import SERVING_ENDPOINT_NAME, NAME

logger = logging.getLogger(__name__)


def apply_to_filter(endpoints_df: pd.DataFrame, applies_to: Dict[str, str]) -> pd.DataFrame:
    """
    Filter endpoints based on policy 'applies_to' criteria.

    Args:
        endpoints_df (pd.DataFrame): DataFrame with endpoint information
        applies_to (Dict[str, str]): Dictionary with filter criteria (e.g., {"serving_endpoint_name": "^databricks-.*"})

    Returns:
        pd.DataFrame: Filtered DataFrame

    Examples:
        >>> df = pd.DataFrame({"name": ["databricks-gpt", "my-model", "databricks-claude"]})
        >>> filtered = apply_to_filter(df, {"serving_endpoint_name": "^databricks-.*"})
        >>> len(filtered)
        2
    """
    if not applies_to:
        logger.warning("No filter criteria provided, returning all endpoints")
        return endpoints_df

    filtered_df = endpoints_df.copy()

    # Handle serving_endpoint_name filter (regex on 'name' column)
    if SERVING_ENDPOINT_NAME in applies_to:
        pattern = applies_to[SERVING_ENDPOINT_NAME]
        logger.info(f"Applying name filter: {pattern}")
        try:
            filtered_df = filtered_df[filtered_df[NAME].str.match(pattern, na=False)]
            logger.info(f"Filter matched {len(filtered_df)} endpoints")
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            raise ValueError(f"Invalid regex pattern: {pattern}")

    # Add more filter types here as needed
    # e.g., filter by tags, state, etc.

    return filtered_df


def matches_filter(endpoint: Dict[str, Any], applies_to: Dict[str, str]) -> bool:
    """
    Check if a single endpoint matches filter criteria.

    Args:
        endpoint (Dict[str, Any]): Endpoint dictionary
        applies_to (Dict[str, str]): Dictionary with filter criteria

    Returns:
        bool: True if endpoint matches all criteria

    Examples:
        >>> endpoint = {"name": "databricks-gpt"}
        >>> matches_filter(endpoint, {"serving_endpoint_name": "^databricks-.*"})
        True
    """
    if not applies_to:
        return True

    # Check serving_endpoint_name filter
    if SERVING_ENDPOINT_NAME in applies_to:
        pattern = applies_to[SERVING_ENDPOINT_NAME]
        endpoint_name = endpoint.get(NAME, "")
        try:
            if not re.match(pattern, endpoint_name):
                return False
        except re.error:
            logger.error(f"Invalid regex pattern: {pattern}")
            return False

    return True
