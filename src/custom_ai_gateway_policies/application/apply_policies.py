
class ApplyPoliciesUseCase:
    """
    Use case for applying a list of policies to all endpoints.
    """
    def __init__(self, endpoint_repo, policies):
        """
        Initialize the use case.
        Args:
            endpoint_repo: Repository to retrieve endpoints from.
            policies (list): List of Policy objects to apply.
        """
        self.endpoint_repo = endpoint_repo  # Adapter to fetch endpoints
        self.policies = policies            # List of policies to apply

    def execute(self):
        """
        Apply all policies to all endpoints.
        Returns:
            list: List of PolicyResult objects for each policy applied to each endpoint.
        """
        endpoints = self.endpoint_repo.list_endpoints()
        results = []
        for endpoint in endpoints:
            for policy in self.policies:
                # Apply each policy to the endpoint
                result = policy.apply(endpoint)
                results.append(result)
        return results
