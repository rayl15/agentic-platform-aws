from typing import Any, Dict, Optional

from agentic_platform.core.observability.provider.base_observability_provider import BaseObservabilityProvider
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter
from logging import Logger

class ObservabilityFacade:
    """
    A unified service to handle all observability concerns.
    This facade class encapsulates all three telemetry signals.
    """
    
    def __init__(self, service_name: str, provider: BaseObservabilityProvider):
        """
        Initialize the observability service.
        
        Args:
            service_name: Name of the service
            provider: An optional pre-configured observability provider
        """
        self.service_name = service_name
        
        # Use provided provider.
        self.provider = provider
        
        # Set up all three signals
        self.provider.setup_tracing()
        self.provider.setup_metrics()
        self.provider.setup_logging()
        
        # Get the components for use
        self.tracer = self.provider.get_tracer(service_name)
        self.meter = self.provider.get_meter(service_name)
        self.logger = self.provider.get_logger(service_name)
        
        # Create commonly used meters
        self.counter_metrics = {}
        self.gauge_metrics = {}
        self.histogram_metrics = {}
    
    def create_counter(self, name: str, description: str, unit: str = "1") -> None:
        """Create a counter metric."""
        self.counter_metrics[name] = self.meter.create_counter(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_gauge(self, name: str, description: str, unit: str = "1") -> None:
        """Create a gauge metric."""
        self.gauge_metrics[name] = self.meter.create_observable_gauge(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_histogram(self, name: str, description: str, unit: str = "1") -> None:
        """Create a histogram metric."""
        self.histogram_metrics[name] = self.meter.create_histogram(
            name=name,
            description=description,
            unit=unit
        )
    
    def increment_counter(self, name: str, value: int = 1, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Increment a counter metric."""
        if name not in self.counter_metrics:
            self.create_counter(name, f"Counter for {name}")
        self.counter_metrics[name].add(value, attributes)
    
    def record_histogram(self, name: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Record a value to a histogram metric."""
        if name not in self.histogram_metrics:
            self.create_histogram(name, f"Histogram for {name}")
        self.histogram_metrics[name].record(value, attributes)
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None, kind=None):
        """Start a new trace span."""
        return self.tracer.start_as_current_span(name, attributes=attributes, kind=kind)
    
    def log(self, level: int, message: str, **kwargs) -> None:
        """Log a message at the specified level."""
        self.logger.log(level, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.logger.critical(message, **kwargs)

    def get_tracer(self) -> Tracer:
        return self.tracer
    
    def get_meter(self) -> Meter:
        return self.meter
    
    def get_logger(self) -> Logger:
        return self.logger
    
# Global instance
_instance: Optional[ObservabilityFacade] = None

def configure_facade(service_name: str, provider: BaseObservabilityProvider) -> 'ObservabilityFacade':
    """
    Configure and set the global ObservabilityFacade instance.
    """
    global _instance
    _instance = ObservabilityFacade(service_name, provider)
    return _instance

def get_facade() -> Optional['ObservabilityFacade']:
    """
    Get the global ObservabilityFacade instance if configured.
    """
    return _instance