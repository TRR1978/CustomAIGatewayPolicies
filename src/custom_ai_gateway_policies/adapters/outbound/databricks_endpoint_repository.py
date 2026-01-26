from databricks.sdk import WorkspaceClient
from custom_ai_gateway_policies.domain.endpoint import Endpoint


class DatabricksEndpointRepository:
    """
    Adapter for retrieving model serving endpoints from Databricks using the SDK.
    """
    def __init__(self, workspace_client: WorkspaceClient):
        """
        Initialize the repository with a Databricks WorkspaceClient.
        Args:
            workspace_client (WorkspaceClient): The Databricks SDK client instance.
        """
        self.client = workspace_client  # Databricks SDK client

    def list_endpoints(self):
        """
        Retrieve all model serving endpoints from Databricks.
        Returns:
            list: List of Endpoint objects.
        """
        endpoints_data = self.client.serving_endpoints.list()
        # Convert each endpoint dict to an Endpoint object
        return [Endpoint(e['id'], e['name'], e) for e in endpoints_data]
