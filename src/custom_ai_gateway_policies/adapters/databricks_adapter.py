import pandas as pd
from databricks.sdk import WorkspaceClient

class DatabricksEndpointAdapter:
    """
    Adapter to list model serving endpoints in Databricks and return them as a pandas DataFrame.
    """
    def __init__(self, workspace_client: WorkspaceClient = None):
        self.client = workspace_client or WorkspaceClient()

    def list_serving_endpoints(self):
        endpoints = self.client.serving_endpoints.list()
        # Convert SDK objects to dictionaries to handle complex nested types
        endpoint_dicts = [ep.as_dict() for ep in endpoints]
        return pd.DataFrame(endpoint_dicts)
    
    def get_serving_endpoint_details(self, endpoint_id: str) -> dict:
        endpoint = self.client.serving_endpoints.get(endpoint_id)
        return endpoint.as_dict()