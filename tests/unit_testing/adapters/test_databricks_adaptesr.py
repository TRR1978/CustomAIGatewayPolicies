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
        def put_ai_gateway(name, rate_limits=None, fallback_config=None, **kwargs):
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
    adapter.w.serving_endpoints.put_ai_gateway = MagicMock()
    config = {"ai_gateway": {"rate_limits": [{"key": "user", "renewal_period": "minute", "calls": 10}]}}
    result = adapter.update_ai_gateway("ep1", config)
    assert result["name"] == "ep1"
    assert result["updated"] is True
    adapter.w.serving_endpoints.put_ai_gateway.assert_called_once()
    _, kwargs = adapter.w.serving_endpoints.put_ai_gateway.call_args
    assert "rate_limits" in kwargs


def test_update_ai_gateway_with_fallback_config():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    adapter.get_serving_endpoint_details = lambda name: {"name": name, "updated": True}
    adapter.w.serving_endpoints.put_ai_gateway = MagicMock()

    config = {
        "ai_gateway": {
            "fallback_config": {"enabled": True}
        }
    }

    result = adapter.update_ai_gateway("ep1", config)

    assert result["name"] == "ep1"
    adapter.w.serving_endpoints.put_ai_gateway.assert_called_once()
    _, kwargs = adapter.w.serving_endpoints.put_ai_gateway.call_args
    assert "fallback_config" in kwargs
    assert getattr(kwargs["fallback_config"], "enabled", None) is True


def test_set_rate_limits_maps_fields():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    rate_limits = [
        {"renewal_period": "minute", "name": "user", "calls": 10},
        {"renewal_period": "minute", "name": "principal", "principal": "spn:abc", "tokens": 50}
    ]

    result = adapter._set_rate_limits(rate_limits)

    assert len(result) == 2
    rl1, rl2 = result
    assert getattr(rl1, "calls", None) == 10
    assert getattr(rl2, "principal", None) == "spn:abc"
    assert getattr(rl2, "tokens", None) == 50


def test_set_rate_limits_defaults_when_missing_fields():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    rate_limits = [
        {"calls": 5},  # missing renewal_period and name
    ]

    result = adapter._set_rate_limits(rate_limits)

    assert len(result) == 1
    rl = result[0]
    assert getattr(rl, "calls", None) == 5


def test_set_rate_limits_unknown_enum_values_fallback():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    rate_limits = [
        {"renewal_period": "unknown", "name": "unknown", "calls": 1}
    ]

    result = adapter._set_rate_limits(rate_limits)

    assert len(result) == 1
    rl = result[0]
    assert getattr(rl, "calls", None) == 1


def test_set_usage_tracking_config_enabled():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())
    usage_tracking = {"enabled": True}

    result = adapter._set_usage_tracking_config(usage_tracking)

    assert getattr(result, "enabled", None) is True


def test_set_usage_tracking_config_missing_enabled():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())

    with pytest.raises(ValueError):
        adapter._set_usage_tracking_config({})


def test_set_usage_tracking_config_enabled_false():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyWorkspaceClient())

    with pytest.raises(ValueError):
        adapter._set_usage_tracking_config({"enabled": "False"})
