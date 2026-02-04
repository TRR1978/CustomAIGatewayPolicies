import pytest
from custom_ai_gateway_policies.domains.result import ValidationError, PolicyResult

def test_validation_error_properties():
    err = ValidationError(key="foo", message="msg", expected=1, found=2)
    assert err.key == "foo"
    assert err.message == "msg"
    assert err.expected == 1
    assert err.found == 2
    assert err.error == "msg"

def test_policy_result_bool():
    result = PolicyResult(is_compliant=True, corrected_config={}, errors=[])
    assert bool(result) is True
    result2 = PolicyResult(is_compliant=False, corrected_config={}, errors=[])
    assert not result2

def test_policy_result_fields():
    result = PolicyResult(is_compliant=False, corrected_config={"foo": 1}, errors=[], endpoint_name="ep1")
    assert result.endpoint_name == "ep1"
    assert result.corrected_config["foo"] == 1
