"""AI Hub wire-schema contracts shared by services that call the AI Hub.

These Pydantic models define the JSON shapes exchanged with the AI Hub billing
and token endpoints. They are currently hand-rolled (and drift) in
product-chatbot and product-search; this is the single source of truth.

Adoption::

    from fortegia_common.aihub import AIHubUsageLedgerEvent, AIHubTokenPayload
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AIHubTokenPayload(BaseModel):
    """The introspected payload of an AI Hub service/runtime token."""

    issuer: str
    audience: str
    subject: str
    tenant_id: str
    tenant_slug: str
    service_key: str
    service_installation_id: str
    origin: str
    customer: dict[str, str] | None = None


class AIHubUsageLedgerEvent(BaseModel):
    """A single usage/billing event posted to the AI Hub usage ledger.

    ``idempotency_key`` makes ingestion safe to retry, so callers can flush
    these off the request path (fire-and-forget or a background outbox).
    """

    tenant_id: str | None = None
    tenant_slug: str | None = None
    source_service: str
    service_key: str
    event_type: str = "usage"
    metric_key: str
    operation: str | None = None
    provider: str | None = None
    model: str | None = None
    quantity: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0
    currency: str = "USD"
    request_id: str | None = None
    session_id: str | None = None
    idempotency_key: str
    metadata: dict[str, object] = Field(default_factory=dict)
    occurred_at: datetime
