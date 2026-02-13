import pytest
import tempfile
import json
import os
from custom_ai_gateway_policies.core.policy_loader import read_policy, validate_policy_structure

def make_policy_file(policy_dict):
    fd, path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(policy_dict, f)
    return path

def test_read_policy_success():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "required"}}}
    path = make_policy_file(policy)
    loaded = read_policy(path)
    assert loaded["policy_name"] == "p"
    os.remove(path)

def test_read_policy_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_policy("nonexistent.json")

def test_read_policy_invalid_json():
    fd, path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write('{invalid json}')
    with pytest.raises(json.JSONDecodeError):
        read_policy(path)
    os.remove(path)

def test_validate_policy_structure_valid():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "required"}}}
    assert validate_policy_structure(policy)

def test_validate_policy_structure_missing_field():
    policy = {"policy_version": "1.0", "rules": {"r": {"type": "required"}}}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)

def test_validate_policy_structure_rules_not_dict():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": []}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)

def test_validate_policy_structure_rule_missing_type():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {}}}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)

def test_validate_policy_structure_rule_invalid_type():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "badtype"}}}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)

def test_validate_policy_structure_fixed_missing_default():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "fixed"}}}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)


def test_validate_policy_structure_regex_missing_pattern():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "regex"}}}
    with pytest.raises(ValueError):
        validate_policy_structure(policy)


def test_validate_policy_structure_regex_valid():
    policy = {"policy_name": "p", "policy_version": "1.0", "rules": {"r": {"type": "regex", "pattern": "^test"}}}
    assert validate_policy_structure(policy)

def test_check_policy_duplicate():
    from custom_ai_gateway_policies.core.policy_loader import check_policy_duplicate
    # No duplicates
    policies = [
        {"policy_name": "p1", "policy_version": "1.0", "rules": {}},
        {"policy_name": "p2", "policy_version": "1.0", "rules": {}}
    ]
    assert not check_policy_duplicate(policies)
    # With duplicate
    policies = [
        {"policy_name": "p1", "policy_version": "1.0", "rules": {}},
        {"policy_name": "p1", "policy_version": "2.0", "rules": {}}
    ]
    assert check_policy_duplicate(policies)
