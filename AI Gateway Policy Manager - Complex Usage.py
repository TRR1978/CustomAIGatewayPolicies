import pandas as pd
from custom_ai_gateway_policies import PolicyManager

manager = PolicyManager()
policies = manager.load_policy_bulk("./example")
results = manager.apply_policy_bulk( policies, dry_mode=True)

report = manager.generate_report(results)
report_df = pd.DataFrame(report)

print(report_df)