import logging
import os
import sys
from typing import Dict, Optional

# Import OpenTelemetry types for type annotations
from opentelemetry import trace
from opentelemetry.trace import Tracer
from opentelemetry import metrics
from opentelemetry.metrics import Meter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from logging import Logger

from agentic_platform.core.observability.provider.base_observability_provider import BaseObservabilityProvider

class OpenTelemetryProvider(BaseObservabilityProvider):
    """
    Implementation of ObservabilityProvider using OpenTelemetry.
    """
    
    def __init__(
        self,
        service_name: str,
        service_version: str = "0.1.0",
        otlp_endpoint: Optional[str] = None,
        additional_attributes: Optional[Dict[str, str]] = None
    ) -> None:
        self.service_name: str = service_name
        self.service_version: str = service_version
        self.otlp_endpoint: str = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        
        # Create base resource with service info
        resource_attributes: Dict[str, str] = {
            "service.name": service_name,
            "service.version": service_version,
        }
        
        # Add any additional attributes
        if additional_attributes:
            resource_attributes.update(additional_attributes)
        
        self.resource: Resource = Resource.create(resource_attributes)
        
        # Initialize providers
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.logger_provider: Optional[LoggerProvider] = None
        
        # Set up all providers during initialization
        self._setup_tracing()
        self._setup_metrics()
        self._setup_logging()

        # Track configured loggers
        self._configured_loggers = set()
    
    def _setup_tracing(self) -> None:
        """Internal method to set up OpenTelemetry tracing."""
        # Create and set global tracer provider
        self.tracer_provider = TracerProvider(resource=self.resource)
        
        # Create OTLP exporter and add it to the tracer provider
        otlp_exporter: OTLPSpanExporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
        self.tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
    
    def _setup_metrics(self) -> None:
        """Internal method to set up OpenTelemetry metrics."""
        # Create OTLP exporter
        otlp_exporter: OTLPMetricExporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
        
        # Create metric reader
        reader: PeriodicExportingMetricReader = PeriodicExportingMetricReader(
            otlp_exporter, export_interval_millis=1000
        )
        
        # Create and set global meter provider
        self.meter_provider = MeterProvider(resource=self.resource, metric_readers=[reader])
        metrics.set_meter_provider(self.meter_provider)
    
    def _setup_logging(self) -> None:
        """Set up OpenTelemetry-aware logging that writes to stdout."""
        # Create the logger provider (still needed for context propagation)
        self.logger_provider = LoggerProvider(resource=self.resource)
        
        # Create a formatter that includes trace context
        self.log_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s - '
            'TraceID=%(otelTraceID)s SpanID=%(otelSpanID)s'
        )
        
        # Create a standard console handler (writes to stdout)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.log_formatter)
        
        # Create the OpenTelemetry handler to inject context
        self.otel_handler = LoggingHandler(
            level=logging.NOTSET,
            logger_provider=self.logger_provider
        )

    
    def get_tracer(self, name: str) -> Tracer:
        """Get a tracer for the given name."""
        return trace.get_tracer(name)
    
    def get_meter(self, name: str) -> Meter:
        """Get a meter for the given name."""
        return metrics.get_meter(name)
    
    def get_logger(self, name: str) -> Logger:
        """Get a logger that writes to stdout with trace context."""
        logger = logging.getLogger(name)
        
        if name not in self._configured_loggers:
            # Add the OpenTelemetry handler for context propagation
            logger.addHandler(self.otel_handler)
            
            # Ensure there's a console handler for stdout logging
            has_console_handler = any(
                isinstance(h, logging.StreamHandler) and 
                h.stream == sys.stdout 
                for h in logger.handlers
            )
            
            if not has_console_handler:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(self.log_formatter)
                logger.addHandler(console_handler)
            
            # Set default level
            if logger.level == logging.NOTSET:
                logger.setLevel(logging.INFO)
            
            self._configured_loggers.add(name)
        
        return logger