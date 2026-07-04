"""Internal service-to-service auth (the ``X-Internal-Key`` contract).

Every internal call between Fortegia services carries an ``X-Internal-Key``
header that the receiver compares against its configured internal key. Today
this verifier is copy-pasted in ai-hub, product-chatbot and product-search under
four different setting names; this is the single canonical implementation.

Adoption (in each service's dependencies module)::

    from fortegia_common.auth import make_internal_key_dependency
    from myservice.config import settings

    require_internal_key = make_internal_key_dependency(
        lambda: settings.INTERNAL_API_KEY
    )

    @router.post("/internal/thing", dependencies=[Depends(require_internal_key)])
    async def thing(): ...

The key MUST be identical across every service that talks to each other (see
docs/SECURITY_AUDIT_PHASE0.md — rotating it is a coordinated change).
"""

from __future__ import annotations

import secrets
from collections.abc import Callable

from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader

internal_key_header = APIKeyHeader(name="X-Internal-Key", auto_error=True)


def make_internal_key_dependency(
    get_expected_key: Callable[[], str],
    *,
    header: APIKeyHeader = internal_key_header,
):
    """Build a FastAPI dependency that fails closed on a missing/mismatched key.

    ``get_expected_key`` is a callable so the current setting value is read per
    request (monkeypatch-friendly in tests, honors runtime key rotation). An
    empty configured key returns 503 (fail-closed) rather than accepting a
    published default.
    """

    async def _require_internal_key(internal_key: str = header) -> str:  # type: ignore[assignment]
        expected = get_expected_key() or ""
        if not expected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Internal key not configured",
            )
        if not secrets.compare_digest(internal_key, expected):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid internal key",
            )
        return internal_key

    return _require_internal_key
