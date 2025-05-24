"""OpenTelemetry configuration and instrumentation."""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from skill_sphere_mcp.config.settings import get_settings

logger = logging.getLogger(__name__)


def setup_telemetry() -> Optional[trace.Tracer]:
    """Configure OpenTelemetry tracing."""
    try:
        settings = get_settings()
        resource = Resource.create({"service.name": settings.otel_service_name})
        provider = TracerProvider(resource=resource)

        # Configure OTLP exporter
        exporter = OTLPSpanExporter(endpoint=settings.otel_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        # Set the global tracer provider
        trace.set_tracer_provider(provider)

        return trace.get_tracer(__name__)
    except (ValueError, RuntimeError) as exc:
        logger.error("Failed to setup OpenTelemetry: %s", exc)
        return None
