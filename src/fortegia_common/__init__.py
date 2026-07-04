"""Fortegia shared service-to-service contracts.

This package holds ONLY the things that must agree across services on the wire:
the internal-key auth check and the AI Hub token/usage-event schemas. It must
never accumulate business logic — that would turn the polyrepo into a
distributed monolith. Add to it only when a new *contract* is shared.
"""

__version__ = "0.1.0"
