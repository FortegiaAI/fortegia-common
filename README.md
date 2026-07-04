# fortegia-common

Shared **service-to-service contracts** for the Fortegia platform. Contracts
only — the internal-key auth check and the AI Hub wire schemas. **Never** put
business logic here; that would couple the services into a distributed monolith.

## Why

These pieces must agree byte-for-byte across services, yet today they're
copy-pasted (and quietly drift) across `product-chatbot`, `ai-hub` and
`product-search`:

- the `X-Internal-Key` verifier (4 setting names for one secret),
- `AIHubTokenPayload` / `AIHubUsageLedgerEvent`.

One source of truth removes the drift.

## What's in it

| Module | Contract |
|---|---|
| `fortegia_common.auth` | `make_internal_key_dependency(get_key)` → a fail-closed FastAPI dependency for `X-Internal-Key`. |
| `fortegia_common.aihub` | `AIHubTokenPayload`, `AIHubUsageLedgerEvent`. |

## Adopt in a service

1. Push this package to `github.com/FortegiaAI/fortegia-common`.
2. In the consuming repo:
   ```bash
   uv add "git+https://github.com/FortegiaAI/fortegia-common@v0.1.0"
   ```
3. Replace the local copy:
   ```python
   # before: local get_internal_key / AIHubUsageLedgerEvent
   from fortegia_common.auth import make_internal_key_dependency
   from fortegia_common.aihub import AIHubUsageLedgerEvent
   require_internal_key = make_internal_key_dependency(lambda: settings.INTERNAL_API_KEY)
   ```

Pin a tag (`@v0.1.0`) per consumer so a contract change is an explicit,
reviewable bump — never a silent break.

## Rules

- Add a module here only when a genuinely *shared contract* appears.
- A change here is a breaking change to every consumer → bump the version and
  update consumers deliberately.
- The runtime `/ready/deep` checks already catch contract drift at deploy time
  (auth mismatch → 401 → red check) — this package prevents the drift at the
  source.
