"""Server-generated, prefixed identifiers (10-api-contracts)."""

import uuid


def _gen(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def new_memory_id() -> str:
    return _gen("mem")


def new_event_id() -> str:
    return _gen("evt")


def new_relation_id() -> str:
    return _gen("rel")
