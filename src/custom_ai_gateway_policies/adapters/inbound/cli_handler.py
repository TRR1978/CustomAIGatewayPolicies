from databricks.sdk import WorkspaceClient
from custom_ai_gateway_policies.adapters.outbound.databricks_endpoint_repository import DatabricksEndpointRepository
from custom_ai_gateway_policies.application.apply_policies import ApplyPoliciesUseCase
# from custom_ai_gateway_policies.domain.policy import Policy1, Policy2  # Define tus políticas concretas

# Ejemplo de handler CLI/script


def main():
    """
    Main entry point for the CLI/script.
    Connects to Databricks, retrieves endpoints, applies policies, and prints results.
    """
    # Create the repository using the Databricks SDK client
    repo = DatabricksEndpointRepository(WorkspaceClient())
    # Add instances of your concrete policies here
    policies = []
    # Create the use case with the repository and policies
    use_case = ApplyPoliciesUseCase(repo, policies)
    # Execute the use case to apply policies to all endpoints
    results = use_case.execute()
    # Print the result for each policy applied to each endpoint
    for r in results:
        print(f"{r.endpoint.name} - {r.policy.__class__.__name__}: {'OK' if r.passed else 'FAIL'}")


if __name__ == "__main__":
    main()
