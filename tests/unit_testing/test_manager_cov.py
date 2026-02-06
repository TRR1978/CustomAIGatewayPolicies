import pytest
from unittest.mock import MagicMock
from custom_ai_gateway_policies.manager import PolicyManager
from custom_ai_gateway_policies.domains.result import ValidationError

def test_apply_policy_not_applies():
    manager = PolicyManager(adapter=MagicMock())
    policy = {'policy_name': 'p', 'policy_version': '1.0', 'rules': {}, 'applies_to': {'name': '^no-match$'}}
    manager.adapter.get_serving_endpoint_details.return_value = {'name': 'endpoint1'}
    result = manager.apply_policy('endpoint1', policy)
    assert result.is_compliant
    assert result.errors == []

def test_apply_policy_update_exception():
    manager = PolicyManager(adapter=MagicMock())
    policy = {'policy_name': 'p', 'policy_version': '1.0', 'rules': {}}
    manager.adapter.get_serving_endpoint_details.return_value = {'name': 'endpoint1'}
    manager.adapter.update_ai_gateway.side_effect = Exception('fail')
    # Make the policy non-compliant so update is triggered
    manager.engine.apply_policy = MagicMock(return_value=MagicMock(is_compliant=False, corrected_config={}, errors=[], endpoint_name='endpoint1'))
    result = manager.apply_policy('endpoint1', policy, dry_mode=False)
    assert any(isinstance(e, ValidationError) and e.key == 'update' for e in result.errors)
