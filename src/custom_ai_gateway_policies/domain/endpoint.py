
class Endpoint:
    """
    Represents a model serving endpoint.
    """
    def __init__(self, id, name, config):
        """
        Initialize an Endpoint instance.
        Args:
            id (str): The unique identifier of the endpoint.
            name (str): The name of the endpoint.
            config (dict): The configuration dictionary for the endpoint.
        """
        self.id = id            # Endpoint unique identifier
        self.name = name        # Endpoint name
        self.config = config    # Endpoint configuration dictionary
