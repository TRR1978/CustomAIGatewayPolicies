import unittest
from unittest.mock import MagicMock
from custom_ai_gateway_policies.application.apply_policies import ApplyPoliciesUseCase
from custom_ai_gateway_policies.domain.endpoint import Endpoint
from custom_ai_gateway_policies.domain.policy import Policy, PolicyResult

class DummyPolicy(Policy):
    def apply(self, endpoint):
        return PolicyResult(endpoint, self, True)

class TestApplyPoliciesUseCase(unittest.TestCase):
    def test_execute(self):
        endpoint_repo = MagicMock()
        endpoint_repo.list_endpoints.return_value = [Endpoint('1', 'ep1', {})]
        policies = [DummyPolicy()]
        use_case = ApplyPoliciesUseCase(endpoint_repo, policies)
        results = use_case.execute()
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].passed)

if __name__ == "__main__":
    unittest.main()
