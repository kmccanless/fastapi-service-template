# OpenTelemetry instrumentation setup
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import os


def setup_otel():
    """Configure OpenTelemetry with auto-instrumentation."""
    resource = Resource(
        attributes={SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "fastapi-hello-world")}
    )

    trace_provider = TracerProvider(resource=resource)

    # Create OTLP Span Exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
    )

    # Add span processor to the trace provider
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global trace provider
    trace.set_tracer_provider(trace_provider)

    return trace_provider
