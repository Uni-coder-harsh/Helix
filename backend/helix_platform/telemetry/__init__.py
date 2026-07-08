import atexit
import os
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

_telemetry_shutdown_registered = False
_telemetry_shutdown_complete = False


def shutdown_telemetry() -> None:
    global _telemetry_shutdown_complete

    if _telemetry_shutdown_complete:
        return

    tracer_provider = trace.get_tracer_provider()
    shutdown_tracer = getattr(tracer_provider, "shutdown", None)
    if callable(shutdown_tracer):
        shutdown_tracer()

    meter_provider = metrics.get_meter_provider()
    shutdown_meter = getattr(meter_provider, "shutdown", None)
    if callable(shutdown_meter):
        shutdown_meter()

    _telemetry_shutdown_complete = True


def setup_telemetry(app_name: str) -> None:
    """Sets up OpenTelemetry tracing and metrics with appropriate exporters."""
    global _telemetry_shutdown_registered

    settings = get_settings()

    # Define resource metadata
    resource = Resource.create({"service.name": app_name, "environment": settings.ENV})

    # 1. Tracing Setup
    tp = TracerProvider(resource=resource)
    trace.set_tracer_provider(tp)

    if os.getenv("HELIX_ENV", "").lower() == "test":
        metrics.set_meter_provider(MeterProvider(resource=resource))
        if not _telemetry_shutdown_registered:
            atexit.register(shutdown_telemetry)
            _telemetry_shutdown_registered = True
        return

    # Try importing OTLP exporter, fallback to console exporter if not installed
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # type: ignore[import-not-found]
            OTLPSpanExporter,
        )

        trace_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except ImportError:
        trace_exporter = ConsoleSpanExporter()  # type: ignore[assignment]

    tp.add_span_processor(SimpleSpanProcessor(trace_exporter))

    # 2. Metrics Setup
    try:
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (  # type: ignore[import-not-found]
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

    if not _telemetry_shutdown_registered:
        atexit.register(shutdown_telemetry)
        _telemetry_shutdown_registered = True


def instrument_app(app: Any) -> None:
    """Instruments a FastAPI application using OpenTelemetry middleware."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)  # type: ignore[unused-ignore]
    except ImportError:
        pass
