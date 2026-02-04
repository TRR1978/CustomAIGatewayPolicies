import pytest
import pandas as pd
from custom_ai_gateway_policies.core.filters import apply_to_filter, matches_filter

def test_apply_to_filter_regex():
    df = pd.DataFrame({"name": ["databricks-gpt", "my-model", "databricks-claude"]})
    filtered = apply_to_filter(df, {"serving_endpoint_name": "^databricks-.*"})
    assert len(filtered) == 2
    assert set(filtered["name"]) == {"databricks-gpt", "databricks-claude"}

def test_apply_to_filter_no_criteria():
    df = pd.DataFrame({"name": ["a", "b"]})
    filtered = apply_to_filter(df, {})
    assert len(filtered) == 2

def test_apply_to_filter_invalid_regex():
    df = pd.DataFrame({"name": ["a", "b"]})
    with pytest.raises(ValueError):
        apply_to_filter(df, {"serving_endpoint_name": "[unclosed"})

def test_matches_filter_true():
    endpoint = {"name": "databricks-gpt"}
    assert matches_filter(endpoint, {"serving_endpoint_name": "^databricks-.*"})

def test_matches_filter_false():
    endpoint = {"name": "my-model"}
    assert not matches_filter(endpoint, {"serving_endpoint_name": "^databricks-.*"})

def test_matches_filter_no_criteria():
    endpoint = {"name": "anything"}
    assert matches_filter(endpoint, {})

def test_matches_filter_invalid_regex():
    endpoint = {"name": "foo"}
    assert not matches_filter(endpoint, {"serving_endpoint_name": "[unclosed"})
