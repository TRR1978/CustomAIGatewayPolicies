import unittest
from custom_ai_gateway_policies.domain.endpoint import Endpoint

class TestEndpoint(unittest.TestCase):
    def test_endpoint_init(self):
        e = Endpoint('id1', 'name1', {'foo': 'bar'})
        self.assertEqual(e.id, 'id1')
        self.assertEqual(e.name, 'name1')
        self.assertEqual(e.config['foo'], 'bar')

if __name__ == "__main__":
    unittest.main()
