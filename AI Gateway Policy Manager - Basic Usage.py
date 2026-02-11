from custom_ai_gateway_policies import PolicyManager

print("Hello! This is a basic usage example of the AI Gateway Policy Manager.")
print("Loading policy from file and applying to a Databricks endpoint in dry mode...")
manager = PolicyManager()

print("Loading policy from './example/ms_policy_databricks.json'...")
policy = manager.load_policy("./example/ms_policy_databricks.json")

print("Applying policy to endpoint 'databricks-claude-opus-4-5' in dry mode...")
result = manager.apply_policy("databricks-claude-opus-4-6", policy, dry_mode=False)

print(f"Policy compliance result for endpoint {result.endpoint_name}:")
print(f"Is compliant: {result.is_compliant}")
print(f"Errors: {result.errors}")
print(f"Corrected config (if any): {result.corrected_config}")
print(f"Policy name: {result.policy_name}")    

