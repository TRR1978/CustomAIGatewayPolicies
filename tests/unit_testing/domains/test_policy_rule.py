import pytest
from custom_ai_gateway_policies.domains.policy import PolicyRule

def test_policy_rule_required():
    rule = PolicyRule(type="required", error_message="Field required")
    assert rule.type == "required"
    assert rule.error_message == "Field required"
    assert rule.default is None

def test_policy_rule_fixed():
    rule = PolicyRule(type="fixed", error_message="Fixed value", default=123)
    assert rule.type == "fixed"
    assert rule.error_message == "Fixed value"
    assert rule.default == 123
