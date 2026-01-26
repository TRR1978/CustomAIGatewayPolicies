
class Policy:
    """
    Abstract base class for all policies.
    Each policy should implement the apply method.
    """
    def apply(self, endpoint):
        """
        Apply the policy to the given endpoint.
        Args:
            endpoint: The endpoint object to which the policy will be applied.
        Returns:
            PolicyResult: The result of the policy evaluation.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")


class PolicyResult:
    """
    Represents the result of applying a policy to an endpoint.
    """
    def __init__(self, endpoint, policy, passed, details=None):
        """
        Initialize a PolicyResult instance.
        Args:
            endpoint: The endpoint to which the policy was applied.
            policy: The policy that was applied.
            passed (bool): Whether the policy passed or failed.
            details (dict, optional): Additional details about the result.
        """
        self.endpoint = endpoint  # Endpoint object
        self.policy = policy      # Policy object
        self.passed = passed      # Boolean indicating if the policy passed
        self.details = details or {}  # Additional result details
