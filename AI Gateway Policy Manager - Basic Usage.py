print("Hola")

from custom_ai_gateway_policies import PolicyManager

manager = PolicyManager()
policy = manager.load_policy("./example/ms_policy_nodatabricks.json")
result = manager.apply_policy("databricks-claude-opus-4-5", policy, dry_mode=True)
result.corrected_config