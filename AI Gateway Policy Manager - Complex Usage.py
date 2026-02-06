from custom_ai_gateway_policies import PolicyManager
import pandas as pd

print("Hello! This is a complex usage example of the AI Gateway Policy Manager.")
print("Loading multiple policies from directory and applying to Databricks endpoints in dry mode...")
manager = PolicyManager()

print("Loading all policies from './example' directory...")
policies = manager.load_policies_bulk("./example")

bulk_results = manager.apply_policies_bulk(policies, dry_mode=True)
for res in bulk_results:     
    print(f"Policy: {res.policy_name} Endpoint: {res.endpoint_name}, Compliant: {res.is_compliant}, Errors: {res.errors}")
    
results_df = pd.DataFrame(bulk_results)
print("\nResults as DataFrame:")
print(results_df)
    
    
json_report = manager.get_compliance_report(bulk_results)
print("\nCompliance report for filtered endpoints:")
print(json_report)
	