"""Regression tests for the shared X-Internal-Key dependency.

v0.1.0 shipped with the header bound as a bare ``APIKeyHeader`` default, which
FastAPI does not recognise as a security scheme — every request 422'd. These
tests pin the deterministic contract: missing/empty/wrong -> 403, valid -> 200,
unset server key -> 503.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fortegia_common.auth import make_internal_key_dependency


def _client(expected_key: str) -> TestClient:
    app = FastAPI()
    dep = make_internal_key_dependency(lambda: expected_key)

    @app.get("/protected", dependencies=[Depends(dep)])
    def protected() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_valid_key_allows_request() -> None:
    resp = _client("secret").get("/protected", headers={"X-Internal-Key": "secret"})
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "headers",
    [
        {},  # missing header — must NOT 422 (the v0.1.0 regression)
        {"X-Internal-Key": ""},  # empty
        {"X-Internal-Key": "wrong"},  # mismatch
    ],
)
def test_missing_or_bad_key_is_forbidden(headers: dict[str, str]) -> None:
    resp = _client("secret").get("/protected", headers=headers)
    assert resp.status_code == 403


def test_unset_server_key_is_unavailable() -> None:
    # Fail closed: an unconfigured key never accepts a published default.
    resp = _client("").get("/protected", headers={"X-Internal-Key": "anything"})
    assert resp.status_code == 503
