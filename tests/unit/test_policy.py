import unittest
from custom_ai_gateway_policies.domain.policy import Policy, PolicyResult
from custom_ai_gateway_policies.domain.endpoint import Endpoint

class DummyPolicy(Policy):
    def apply(self, endpoint):
        return PolicyResult(endpoint, self, True, {'checked': True})

class TestPolicy(unittest.TestCase):
    def test_policy_apply(self):
        endpoint = Endpoint('1', 'test', {})
        policy = DummyPolicy()
        result = policy.apply(endpoint)
        self.assertTrue(result.passed)
        self.assertEqual(result.endpoint, endpoint)
        self.assertEqual(result.details['checked'], True)

    def test_policy_result(self):
        endpoint = Endpoint('2', 'test2', {})
        policy = DummyPolicy()
        result = PolicyResult(endpoint, policy, False, {'reason': 'fail'})
        self.assertFalse(result.passed)
        self.assertEqual(result.details['reason'], 'fail')

if __name__ == "__main__":
    unittest.main()
