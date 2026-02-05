import pytest
from custom_ai_gateway_policies.core.policy_engine import PolicyEngine
from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError

@pytest.fixture
def engine():
    return PolicyEngine()

@pytest.mark.parametrize("policy_key,expected", [
    ("ai_gateway.rate_limits.user.requests_per_minute", {
        'is_rate_limit': True,
        'key_name': 'user',
        'field': 'requests_per_minute',
        'renewal_period': 'minute'
    }),
    ("ai_gateway.rate_limits.user_group.admin.requests_per_hour", {
        'is_rate_limit': True,
        'key_name': 'user_group',
        'principal': 'admin',
        'field': 'requests_per_hour',
        'renewal_period': 'hour'
    }),
    ("ai_gateway.config", {'is_rate_limit': False}),
])
def test_parse_rate_limit_key(engine, policy_key, expected):
    assert engine.parse_rate_limit_key(policy_key) == expected

@pytest.mark.parametrize("data,key,expected", [
    ({'a': {'b': 1}}, 'a.b', (True, 1)),
    ({'a': {'b': 1}}, 'a.c', (False, None)),
    ({'a': 2}, 'a.b', (False, None)),
])
def test_search_nested_key(engine, data, key, expected):
    assert engine.search_nested_key(data, key) == expected

def test_apply_policy_compliant(engine):
    rules = {
        'ai_gateway.rate_limits.user.requests_per_minute': {
            'type': 'fixed',
            'default': 100,
            'error_message': 'User rate limit must be 100'
        },
        'ai_gateway.config.enabled': {
            'type': 'required',
            'default': True,
            'error_message': 'Config must be enabled'
        }
    }
    config = {
        'ai_gateway': {
            'rate_limits': [
                {'key': 'user', 'calls': 100, 'renewal_period': 'minute'}
            ],
            'config': {'enabled': True}
        }
    }
    policy_name = 'test_policy'
    result = engine.apply_policy(policy_name, rules, config)
    assert isinstance(result, PolicyResult)
    assert result.is_compliant
    assert result.errors == []
    assert result.corrected_config['ai_gateway']['rate_limits'][0]['calls'] == 100
def test_apply_policy_noncompliant_and_correction(engine):
    rules = {
        'ai_gateway.rate_limits.user.requests_per_minute': {
            'type': 'fixed',
            'default': 50,
            'error_message': 'User rate limit must be 50'
        },
        'ai_gateway.config.enabled': {
            'type': 'required',
            'default': True,
            'error_message': 'Config must be enabled'
        }
    }
    config = {
        'ai_gateway': {
            'rate_limits': [
                {'key': 'user', 'calls': 100, 'renewal_period': 'minute'}
            ],
            'config': {'enabled': False}
        }
    }
    policy_name = 'test_policy'
    result = engine.apply_policy(policy_name, rules, config)
    assert not result.is_compliant
    assert len(result.errors) == 1
    # Correction applied
    assert result.corrected_config['ai_gateway']['rate_limits'][0]['calls'] == 50
def test_apply_policy_missing_rate_limit_entry(engine):
    rules = {
        'ai_gateway.rate_limits.user_group.admin.requests_per_minute': {
            'type': 'fixed',
            'default': 10,
            'error_message': 'Admin rate limit must be 10'
        }
    }
    config = {
        'ai_gateway': {
            'rate_limits': [
                {'key': 'user', 'calls': 100, 'renewal_period': 'minute'}
            ]
        }
    }
    policy_name = 'test_policy'
    result = engine.apply_policy(policy_name, rules, config)
    assert not result.is_compliant
    assert len(result.errors) == 1
    # Correction: new entry added
    admin_limits = [rl for rl in result.corrected_config['ai_gateway']['rate_limits'] if rl.get('principal') == 'admin']
    assert admin_limits and admin_limits[0]['calls'] == 10
def test_apply_policy_internal_error(engine, mocker):
    # Simulate error in _apply_single_rule
    rules = {'ai_gateway.config.enabled': {'type': 'required', 'default': True}}
    config = {'ai_gateway': {'config': {'enabled': True}}}
    mocker.patch.object(engine, '_apply_single_rule', side_effect=Exception('fail'))
    policy_name = 'test_policy'
    result = engine.apply_policy(policy_name, rules, config)
    assert not result.is_compliant
    assert len(result.errors) == 1
    assert 'Internal error' in result.errors[0].message
    assert not result.is_compliant
    assert len(result.errors) == 1
    assert 'Internal error' in result.errors[0].message

def test_apply_policy_result_fields(engine):
    rules = {
        'ai_gateway.rate_limits.user.requests_per_minute': {
            'type': 'fixed',
            'default': 100,
            'error_message': 'User rate limit must be 100'
        }
    }
    config = {
        'name': 'endpoint1',
        'ai_gateway': {
            'rate_limits': [
                {'key': 'user', 'calls': 100, 'renewal_period': 'minute'}
            ]
        }
    }
    policy_name = 'test_policy'
    result = engine.apply_policy(policy_name, rules, config)
    assert result.policy_name == policy_name
    assert result.endpoint_name == 'endpoint1'
