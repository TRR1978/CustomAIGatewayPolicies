import unittest
from unittest.mock import patch, MagicMock
from custom_ai_gateway_policies.adapters.inbound import cli_handler

class TestCliHandler(unittest.TestCase):
    @patch('custom_ai_gateway_policies.adapters.inbound.cli_handler.DatabricksEndpointRepository')
    @patch('custom_ai_gateway_policies.adapters.inbound.cli_handler.WorkspaceClient')
    @patch('custom_ai_gateway_policies.adapters.inbound.cli_handler.ApplyPoliciesUseCase')
    def test_main(self, mock_usecase, mock_wsclient, mock_repo):
        mock_instance = MagicMock()
        mock_instance.execute.return_value = []
        mock_usecase.return_value = mock_instance
        cli_handler.main()
        mock_repo.assert_called_once()
        mock_usecase.assert_called_once()
        mock_instance.execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()
