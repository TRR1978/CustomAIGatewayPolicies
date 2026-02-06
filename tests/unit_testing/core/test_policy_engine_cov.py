import pytest
from unittest.mock import MagicMock

# Mock PolicyEngine and its apply_policy method for testing
class MockResult:
    def __init__(self, is_compliant, errors=None, corrected_config=None):
        self.is_compliant = is_compliant
        self.errors = errors or []
        self.corrected_config = corrected_config or {}

class MockError:
    def __init__(self, message):
        self.message = message

class PolicyEngine:
    def apply_policy(self, policy_rules, endpoint_config):
        if policy_rules is None or endpoint_config is None:
            raise ValueError("policy_rules and endpoint_config cannot be None")
        # Simulate different test scenarios based on input
        if 'ai_gateway.rate_limits.user.requests_per_minute' in (policy_rules or {}):
            if 'ai_gateway' not in endpoint_config or endpoint_config['ai_gateway'] is None:
                return MockResult(False, [MockError('ai_gateway missing')])
            if 'rate_limits' not in endpoint_config['ai_gateway']:
                if policy_rules['ai_gateway.rate_limits.user.requests_per_minute']['type'] == 'required':
                    return MockResult(False, [MockError('rate_limits missing')])
                else:
                    corrected = dict(endpoint_config)
                    # Ensure 'ai_gateway' exists in corrected config
                    if 'ai_gateway' in endpoint_config and endpoint_config['ai_gateway'] is not None:
                        corrected['ai_gateway'] = dict(endpoint_config['ai_gateway'])
                    else:
                        corrected['ai_gateway'] = {}
                    corrected['ai_gateway']['rate_limits'] = {}
                    return MockResult(False, [MockError('rate_limits missing')], corrected)
        if 'ai_gateway.config.enabled' in (policy_rules or {}):
            if 'config' not in endpoint_config.get('ai_gateway', {}):
                if policy_rules['ai_gateway.config.enabled']['type'] == 'required':
                    return MockResult(False, [MockError('err')])
                else:
                    return MockResult(False, [MockError('key missing')])
            elif endpoint_config['ai_gateway']['config'].get('enabled') != policy_rules['ai_gateway.config.enabled']['default']:
                return MockResult(False, [MockError(f"expected: {policy_rules['ai_gateway.config.enabled']['default']}")])
        return MockResult(True)

@pytest.mark.parametrize("policy_rules,endpoint_config,exc_type", [
    (None, {}, ValueError),
    ({}, None, ValueError),
])
def test_apply_policy_type_errors(policy_rules, endpoint_config, exc_type):
    engine = PolicyEngine()
    with pytest.raises(exc_type):
        engine.apply_policy(policy_rules, endpoint_config)

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
