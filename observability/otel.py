from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


@lru_cache(maxsize=1)
def configure_otel() -> None:
    """
    Configure OpenTelemetry tracing (no-op if not enabled).

    Enable by setting:
    - OTEL_EXPORTER_OTLP_ENDPOINT (recommended), e.g. https://collector:4318
    - OTEL_EXPORTER_OTLP_HEADERS (optional), e.g. "Authorization=Bearer xxx"
    - OTEL_SERVICE_NAME (optional)
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return

    # Avoid double-initialization if a platform (or us) already set an SDK provider.
    if isinstance(trace.get_tracer_provider(), TracerProvider):
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "hf-agents-unit4")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Prefer OTLP/HTTP exporter for easy hosted collectors.
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    headers_env = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    headers: dict[str, str] | None = None
    if headers_env.strip():
        parsed: dict[str, str] = {}
        for part in headers_env.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                parsed[k.strip()] = v.strip()
        headers = parsed or None

    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Optional HTTP client instrumentation
    if _truthy(os.getenv("OTEL_INSTRUMENT_REQUESTS", "true")):
        try:
            from opentelemetry.instrumentation.requests import RequestsInstrumentor

            RequestsInstrumentor().instrument()
        except Exception:
            # Instrumentation is best-effort; don't break runtime.
            pass


def get_tracer():
    configure_otel()
    return trace.get_tracer("hf-agents-unit4")


def span_attributes_from(metadata: dict[str, Any] | None) -> dict[str, Any]:
    md = metadata or {}
    attrs: dict[str, Any] = {}
    for k in ("task_id", "username", "space_id", "model", "langsmith_project"):
        if k in md and md[k] is not None:
            attrs[f"app.{k}"] = str(md[k])
    return attrs

