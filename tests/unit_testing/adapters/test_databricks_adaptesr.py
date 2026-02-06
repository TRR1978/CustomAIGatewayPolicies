import pytest
from unittest.mock import MagicMock
import pandas as pd
from custom_ai_gateway_policies.adapters.databricks_adapter import DatabricksEndpointAdapter

class DummyWorkspaceClient:
    class serving_endpoints:
        @staticmethod
        def list():
            return [MagicMock(as_dict=lambda: {"name": "ep1"}), MagicMock(as_dict=lambda: {"name": "ep2"})]
        @staticmethod
        def get(name):
            return MagicMock(as_dict=lambda: {"name": name, "details": "info"})
        @staticmethod
        def put_ai_gateway(name, rate_limits):
            return None

def test_list_endpoints():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    df = adapter.list_endpoints()
    assert isinstance(df, pd.DataFrame)
    assert set(df["name"]) == {"ep1", "ep2"}

def test_get_serving_endpoint_details():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    details = adapter.get_serving_endpoint_details("ep1")
    assert details["name"] == "ep1"
    assert details["details"] == "info"

def test_get_endpoints_by_filter():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    # Patch list_endpoints to return a DataFrame with a 'name' column
    adapter.list_endpoints = lambda: pd.DataFrame([
        {"name": "databricks-foo"},
        {"name": "other-bar"}
    ])
    filtered = adapter.get_endpoints_by_filter({"name": "^databricks-.*"})
    assert len(filtered) == 1
    assert filtered[0]["name"] == "databricks-foo"

def test_update_ai_gateway():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    # Patch get_serving_endpoint_details to return a known value
    adapter.get_serving_endpoint_details = lambda name: {"name": name, "updated": True}
    config = {"ai_gateway": {"rate_limits": [{"key": "user", "renewal_period": "minute", "calls": 10}]}}
    result = adapter.update_ai_gateway("ep1", config)
    assert result["name"] == "ep1"
    assert result["updated"] is True
