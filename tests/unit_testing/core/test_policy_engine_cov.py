import pytest
from custom_ai_gateway_policies.core.policy_engine import PolicyEngine

@pytest.mark.parametrize("rules_policy,endpoint_config,exc_type", [
    (None, {}, ValueError),
    ({}, None, ValueError),
])
def test_apply_policy_type_errors(rules_policy, endpoint_config, exc_type):
    engine = PolicyEngine()
    with pytest.raises(exc_type):
        engine.apply_policy(rules_policy, endpoint_config)

def test_apply_rate_limit_required_missing_ai_gateway():
    engine = PolicyEngine()
    rules = {'ai_gateway.rate_limits.user.requests_per_minute': {'type': 'required', 'default': 1, 'error_message': 'err'}}
    config = {}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    assert 'ai_gateway missing' in result.errors[0].message

def test_apply_rate_limit_required_missing_rate_limits():
    engine = PolicyEngine()
    rules = {'ai_gateway.rate_limits.user.requests_per_minute': {'type': 'required', 'default': 1, 'error_message': 'err'}}
    config = {'ai_gateway': {}}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    assert 'rate_limits missing' in result.errors[0].message

def test_apply_rate_limit_fixed_missing_rate_limits():
    engine = PolicyEngine()
    rules = {'ai_gateway.rate_limits.user.requests_per_minute': {'type': 'fixed', 'default': 1, 'error_message': 'err'}}
    config = {'ai_gateway': {}}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    # Should not raise, should add empty rate_limits
    assert 'rate_limits' in result.corrected_config['ai_gateway']

def test_apply_generic_rule_required_missing():
    engine = PolicyEngine()
    rules = {'ai_gateway.config.enabled': {'type': 'required', 'default': True, 'error_message': 'err'}}
    config = {'ai_gateway': {}}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    assert 'err' in result.errors[0].message

def test_apply_generic_rule_fixed_missing():
    engine = PolicyEngine()
    rules = {'ai_gateway.config.enabled': {'type': 'fixed', 'default': True, 'error_message': 'err'}}
    config = {'ai_gateway': {}}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    assert 'key missing' in result.errors[0].message

def test_apply_generic_rule_fixed_wrong_value():
    engine = PolicyEngine()
    rules = {'ai_gateway.config.enabled': {'type': 'fixed', 'default': True, 'error_message': 'err'}}
    config = {'ai_gateway': {'config': {'enabled': False}}}
    result = engine.apply_policy(rules, config)
    assert not result.is_compliant
    assert 'expected: True' in result.errors[0].message
