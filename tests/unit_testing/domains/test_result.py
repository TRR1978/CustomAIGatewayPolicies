import pytest
from custom_ai_gateway_policies.domains.result import ValidationError, PolicyResult

def test_validation_error_properties():
    err = ValidationError(key="foo", message="msg", expected=1, found=2)
    assert err.key == "foo"
    assert err.message == "msg"
    assert err.expected == 1
    assert err.found == 2
    assert err.error == "msg"

def test_policy_result_requires_policy_and_endpoint_name():
    # Both policy_name and endpoint_name are required
    result = PolicyResult(
        is_compliant=True,
        corrected_config={},
        errors=[],
        policy_name="test_policy",
        endpoint_name="ep1"
    )
    assert result.policy_name == "test_policy"
    assert result.endpoint_name == "ep1"

def test_policy_result_bool():
    result = PolicyResult(is_compliant=True, corrected_config={}, errors=[], policy_name="p", endpoint_name="e")
    assert bool(result) is True
    result2 = PolicyResult(is_compliant=False, corrected_config={}, errors=[], policy_name="p", endpoint_name="e")
    assert not result2

def test_policy_result_fields():
    result = PolicyResult(is_compliant=False, corrected_config={"foo": 1}, errors=[], policy_name="p", endpoint_name="ep1")
    assert result.endpoint_name == "ep1"
    assert result.policy_name == "p"
    assert result.corrected_config["foo"] == 1
