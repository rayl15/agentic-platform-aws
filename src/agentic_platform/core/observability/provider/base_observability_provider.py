from abc import ABC, abstractmethod

class BaseObservabilityProvider(ABC):
    """
    Abstract base class for observability providers.
    Implementations can switch out the underlying tooling.
    """
    @abstractmethod
    def get_tracer(self, name: str):
        """Get a tracer for creating spans."""
        pass
    
    @abstractmethod
    def get_meter(self, name: str):
        """Get a meter for recording metrics."""
        pass
    
    @abstractmethod
    def get_logger(self, name: str):
        """Get a logger for recording logs."""
        pass