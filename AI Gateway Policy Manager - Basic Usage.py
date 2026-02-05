from custom_ai_gateway_policies import PolicyManager

print("Hello! This is a basic usage example of the AI Gateway Policy Manager.")
print("Loading policy from file and applying to a Databricks endpoint in dry mode...")
manager = PolicyManager()

print("Loading policy from './example/ms_policy_nodatabricks.json'...")
policy = manager.load_policy("./example/ms_policy_nodatabricks.json")

print("Applying policy to endpoint 'databricks-claude-opus-4-5' in dry mode...")
result = manager.apply_policy("databricks-claude-opus-4-5", policy, dry_mode=True)

print(f"Policy compliance result for endpoint 'databricks-claude-opus-4-5':")
print(f"Is compliant: {result.is_compliant}")
print(f"Errors: {result.errors}")
print(f"Corrected config (if any): {result.corrected_config}")

print("\nApplying policy to all endpoints with name starting with 'databricks-' in dry mode...")
bulk_results = manager.apply_policy_bulk(policy, filter_dict={"name": "^databricks-.*"}, dry_mode=True)
for res in bulk_results:     
    print(f"Endpoint: {res.endpoint_name}, Compliant: {res.is_compliant}, Errors: {res.errors}")
    
    
json_report = manager.get_compliance_report(bulk_results)
print("\nCompliance report for filtered endpoints:")
print(json_report)
    

