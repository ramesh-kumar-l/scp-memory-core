"""Observability wiring (Phase 6, 17-observability-model).

Metrics (Prometheus) and structured JSON logs ship inline with every feature
(see ``metrics.py`` / ``logging_config.py``). This package adds the Phase-6
consolidation: distributed tracing (OpenTelemetry) and the deploy-time stack
(Prometheus + Grafana + Tempo + SLO rules under ``deploy/observability/``).
"""

from scp_memory.observability.tracing import configure_tracing

__all__ = ["configure_tracing"]
