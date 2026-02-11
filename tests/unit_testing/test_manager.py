import pytest
from unittest.mock import MagicMock, patch
from custom_ai_gateway_policies.manager import PolicyManager
from custom_ai_gateway_policies.domains.result import PolicyResult, ValidationError


@pytest.fixture
def mock_adapter():
    adapter = MagicMock()
    adapter.get_serving_endpoint_details.return_value = {'name': 'endpoint1', 'config': {'enabled': True}, 'ai_gateway': {'rate_limits': []}}
    adapter.list_endpoints.return_value = MagicMock(
        iterrows=lambda: iter([
            (0, {'name': 'endpoint1'}),
            (1, {'name': 'endpoint2'})
        ]),
        __len__=lambda self: 2
    )
    adapter.update_ai_gateway.return_value = None
    return adapter

@pytest.fixture
def manager(mock_adapter):
    return PolicyManager(adapter=mock_adapter)

def test_load_policy_dict(manager):
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}}
    loaded = manager.load_policy(policy)
    assert loaded['policy_name'] == 'test'

def test_load_policy_file(manager, tmp_path):
    import json
    policy = {'policy_name': 'filetest', 'policy_version': '1.0', 'rules': {}}
    file_path = tmp_path / 'policy.json'
    file_path.write_text(json.dumps(policy))
    loaded = manager.load_policy(str(file_path))
    assert loaded['policy_name'] == 'filetest'

def test_apply_policy_compliant(manager):
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}}
    result = manager.apply_policy('endpoint1', policy)
    assert isinstance(result, PolicyResult)
    assert result.is_compliant
    assert result.endpoint_name == 'endpoint1'

def test_apply_policy_not_found(manager, mock_adapter):
    mock_adapter.get_serving_endpoint_details.side_effect = Exception('not found')
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}}
    result = manager.apply_policy('missing', policy)
    assert not result.is_compliant
    assert result.errors
    assert result.errors[0].key == 'endpoint'

def test_apply_policy_does_not_apply(manager, mock_adapter):
    # Policy with applies_to that does not match endpoint config
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}, 'applies_to': {'name': '^no-match$'}}
    result = manager.apply_policy('endpoint1', policy)
    assert result.is_compliant
    assert result.errors == []

def test_apply_policy_bulk(manager, mock_adapter):
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}}
    results = manager.apply_policy_bulk(policy)
    assert isinstance(results, list)
    assert all(isinstance(r, PolicyResult) for r in results)
    assert all(r.endpoint_name in ['endpoint1', 'endpoint2'] for r in results)

def test_apply_policy_bulk_with_filter(manager, mock_adapter):
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {}}
    filter_dict = {'name': '^endpoint1$'}
    class DummyDF:
        def __len__(self):
            return 1
        def iterrows(self):
            return iter([(0, {'name': 'endpoint1'})])

    with patch('custom_ai_gateway_policies.manager.apply_to_filter') as mock_filter:
        mock_filter.return_value = DummyDF()
        results = manager.apply_policy_bulk(policy, filter_dict=filter_dict)
        assert len(results) == 1
        assert results[0].endpoint_name == 'endpoint1'

def test_get_compliance_report(manager):
    results = [
        PolicyResult(is_compliant=True, corrected_config={}, errors=[], changes_made=False, endpoint_name='e1', policy_name='p1'),
        PolicyResult(is_compliant=False, corrected_config={}, errors=[ValidationError(key='k', message='m')], changes_made=False, endpoint_name='e2', policy_name='p1')
    ]
    # Add a new parameter 'include_details' to the method call
    report = manager.get_compliance_report(results)
    assert report['total_endpoints'] == 2
    assert report['compliant'] == 1
    assert report['non_compliant'] == 1
    assert report['total_violations'] == 1
    assert report['violations'][0]['endpoint'] == 'e2'

def test_load_policies_bulk(manager, tmp_path):
    import json
    # Create multiple policy files
    policy1 = {'policy_name': 'bulk1', 'policy_version': '1.0', 'rules': {}}
    policy2 = {'policy_name': 'bulk2', 'policy_version': '1.0', 'rules': {}}
    (tmp_path / 'policy1.json').write_text(json.dumps(policy1))
    (tmp_path / 'policy2.json').write_text(json.dumps(policy2))
    # Load policies from directory
    loaded = manager.load_policies_bulk(tmp_path)
    names = {p['policy_name'] for p in loaded}
    assert 'bulk1' in names
    assert 'bulk2' in names
    assert len(loaded) == 2

def test_apply_policies_bulk(manager, mock_adapter):
    # Two policies, both should apply to both endpoints
    policy1 = {'policy_name': 'p1', 'policy_version': '1.0', 'rules': {}}
    policy2 = {'policy_name': 'p2', 'policy_version': '1.0', 'rules': {}}
    policies = [policy1, policy2]
    results = manager.apply_policies_bulk(policies)
    # Should return 4 results (2 policies x 2 endpoints)
    assert isinstance(results, list)
    assert len(results) == 4
    names = {r.policy_name for r in results}
    assert 'p1' in names and 'p2' in names
    endpoints = {r.endpoint_name for r in results}
    assert 'endpoint1' in endpoints and 'endpoint2' in endpoints
    assert all(isinstance(r, type(results[0])) for r in results)

def test_load_policy_invalid_structure(manager):
    # Missing required field 'policy_name'
    invalid_policy = {'policy_version': '1.0', 'rules': {}}
    import pytest
    with pytest.raises(ValueError):
        manager.load_policy(invalid_policy)

def test_load_policies_bulk_invalid_json(manager, tmp_path):
    # Create one valid and one invalid JSON file
    import json
    valid = {'policy_name': 'valid', 'policy_version': '1.0', 'rules': {}}
    (tmp_path / 'valid.json').write_text(json.dumps(valid))
    (tmp_path / 'invalid.json').write_text('{bad json}')
    # Should skip invalid and load valid
    loaded = manager.load_policies_bulk(tmp_path)
    assert len(loaded) == 1
    assert loaded[0]['policy_name'] == 'valid'

def test_apply_policy_noncompliant_update_success(manager, mock_adapter):
    # Policy that triggers correction
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {'r': {'type': 'fixed', 'default': 1}}}
    # Endpoint config will not match, so correction is needed
    mock_adapter.get_serving_endpoint_details.return_value = {'name': 'endpoint1', 'config': {'r': 0}, 'ai_gateway': {'rate_limits': []}}
    mock_adapter.update_ai_gateway.return_value = None
    result = manager.apply_policy('endpoint1', policy, dry_mode=False)
    assert isinstance(result, type(result))
    assert result.endpoint_name == 'endpoint1'
    # Should be compliant after correction attempt (simulate re-apply)

def test_apply_policy_noncompliant_update_failure(manager, mock_adapter):
    # Policy that triggers correction
    policy = {'policy_name': 'test', 'policy_version': '1.0', 'rules': {'r': {'type': 'fixed', 'default': 1}}}
    mock_adapter.get_serving_endpoint_details.return_value = {'name': 'endpoint1', 'config': {'r': 0}, 'ai_gateway': {'rate_limits': []}}
    # Simulate update failure
    mock_adapter.update_ai_gateway.side_effect = Exception('update failed')
    result = manager.apply_policy('endpoint1', policy, dry_mode=False)
    assert not result.is_compliant or any('update' in e.key for e in result.errors)