import pytest
from unittest.mock import MagicMock
from custom_ai_gateway_policies.adapters.databricks_adapter import DatabricksEndpointAdapter

class DummyW:
    def __init__(self):
        self.serving_endpoints = MagicMock()

def test_get_serving_endpoint_details_exception():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyW())
    adapter.w.serving_endpoints.get.side_effect = Exception('fail')
    with pytest.raises(Exception):
        adapter.get_serving_endpoint_details('foo')

def test_update_ai_gateway_no_rate_limits():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyW())
    config = {'ai_gateway': {}}
    with pytest.raises(ValueError):
        adapter.update_ai_gateway('foo', config)

def test_update_ai_gateway_exception():
    adapter = DatabricksEndpointAdapter(workspace_client=DummyW())
    config = {'ai_gateway': {'rate_limits': [{'key': 'user', 'calls': 1, 'renewal_period': 'minute'}]}}
    adapter.w.serving_endpoints.put_ai_gateway.side_effect = Exception('fail')
    with pytest.raises(Exception):
        adapter.update_ai_gateway('foo', config)

def test_get_endpoints_by_filter_no_name(monkeypatch):
    adapter = DatabricksEndpointAdapter(workspace_client=DummyW())
    df = MagicMock()
    df.to_dict.return_value = [{'name': 'a'}]
    adapter.list_endpoints = MagicMock(return_value=df)
    result = adapter.get_endpoints_by_filter({})
    assert result == [{'name': 'a'}]
