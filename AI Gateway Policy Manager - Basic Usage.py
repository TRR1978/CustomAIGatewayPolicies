from custom_ai_gateway_policies import PolicyManager

print("Hello! This is a basic usage example of the AI Gateway Policy Manager.")
print("Loading policy from file and applying to a Databricks endpoint in dry mode...")
manager = PolicyManager()

print("Loading policy from './example/ms_policy_databricks.json'...")
policy = manager.load_policy("./example/ms_policy_databricks.json")

print("Applying policy to endpoint 'databricks-claude-sonnet-4-5' in dry mode...")
result = manager.apply_policy("databricks-claude-sonnet-4-5", policy, dry_mode=False)

print(f"Policy compliance result for endpoint {result.endpoint_name}:")
print(f"Is compliant: {result.is_compliant}")
print(f"Errors: {result.errors}")
print(f"Corrected config (if any): {result.corrected_config}")
print(f"Policy name: {result.policy_name}")    
print(f"Changes made: {result.changes_made}")

bulk_results = manager.apply_policy_bulk(policy, filter_dict={"name": "^databricks-.*"}, dry_mode=True)
for res in bulk_results:     
    print(f"Policy: {res.policy_name} Endpoint: {res.endpoint_name}, Compliant: {res.is_compliant}, Errors: {res.errors}, Changes made: {res.changes_made}")
    
    
json_report = manager.get_compliance_report(bulk_results)
print("\nCompliance report for filtered endpoints:")
print(json_report)   