import unittest
from unittest.mock import MagicMock
from custom_ai_gateway_policies.adapters.outbound.databricks_endpoint_repository import DatabricksEndpointRepository
from custom_ai_gateway_policies.domain.endpoint import Endpoint

class TestDatabricksEndpointRepository(unittest.TestCase):
    def test_list_endpoints(self):
        mock_client = MagicMock()
        mock_client.serving_endpoints.list.return_value = [
            {'id': '1', 'name': 'ep1'},
            {'id': '2', 'name': 'ep2'}
        ]
        repo = DatabricksEndpointRepository(mock_client)
        endpoints = repo.list_endpoints()
        self.assertEqual(len(endpoints), 2)
        self.assertIsInstance(endpoints[0], Endpoint)
        self.assertEqual(endpoints[0].name, 'ep1')

if __name__ == "__main__":
    unittest.main()
