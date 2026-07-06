from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from helix_platform.config import get_settings


def setup_telemetry(app_name: str) -> None:
    """Sets up OpenTelemetry tracing and metrics with appropriate exporters."""
    settings = get_settings()

    # Define resource metadata
    resource = Resource.create({"service.name": app_name, "environment": settings.ENV})

    # 1. Tracing Setup
    tp = TracerProvider(resource=resource)

    # Try importing OTLP exporter, fallback to console exporter if not installed
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        trace_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except ImportError:
        trace_exporter = ConsoleSpanExporter()  # type: ignore[assignment]

    tp.add_span_processor(SimpleSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tp)

    # 2. Metrics Setup
    try:
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )

        metric_exporter = OTLPMetricExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT
        )
    except ImportError:
        metric_exporter = ConsoleMetricExporter()  # type: ignore[assignment]

    reader = PeriodicExportingMetricReader(metric_exporter)
    mp = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(mp)


def instrument_app(app: Any) -> None:
    """Instruments a FastAPI application using OpenTelemetry middleware."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)  # type: ignore[unused-ignore]
    except ImportError:
        pass
