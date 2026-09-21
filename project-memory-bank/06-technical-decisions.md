# 06 — Technical Decisions

**Status:** Active · **Phase:** 0 · **Last updated:** 2026-06-20

Narrative rationale for the **locked stack**. Each decision has a formal entry in
[25-adr-log](25-adr-log.md) (ADR-001…010, all **Accepted**).

## Locked Stack

| Concern | Decision | Why | Alternatives considered |
|---|---|---|---|
| Language | **Python 3.11+** | Dominant in AI/ML; rich ecosystem; fast to build SDKs | Go, Rust (faster, but slower iteration and weaker AI ecosystem) |
| API framework | **FastAPI** | Async, typed, OpenAPI out of the box; pairs with Pydantic | Flask (less typing), Django (too heavy), Litestar (smaller community) |
| Validation | **Pydantic v2** | First-class FastAPI integration; fast; clear contracts | dataclasses + manual validation, attrs |
| ORM | **SQLAlchemy 2.x** | Mature; backend-portable (SQLite↔Postgres); async support | Tortoise, Peewee, raw SQL (less portable/maintainable) |
| Database (MVP) | **SQLite** | Zero-config; local-first; perfect for on-device + dev | Postgres from day one (heavier for MVP/on-device) |
| Database (scale) | **PostgreSQL** | Battle-tested; pgvector option; scales | MySQL, cloud-proprietary stores |
| Vector store | **Qdrant** | Open source; strong filtering; local + cloud; good Python client | Pinecone (closed), Weaviate, Milvus, pgvector (start simple) |
| Graph layer | **NetworkX** | Pure-Python; zero infra; fine for MVP relations | Neo4j (powerful but heavy) — deferred as optional later |
| Observability | **OpenTelemetry + Prometheus + Grafana** | Vendor-neutral standard; portable | Proprietary APM, ad-hoc logging |
| Testing | **Pytest (+ integration + benchmark)** | Standard; fixtures; plugin ecosystem | unittest, nose |

## Decision Principles Applied

- **Local-first / portable:** SQLite + Qdrant + NetworkX all run on a laptop and
  on-device; same domain model scales to Postgres + Qdrant cluster.
- **Start simple, keep doors open:** the relational store is the source of truth
  and is backend-portable; the vector store is a derived, swappable index.
- **Open core:** every chosen component is open source and self-hostable.

## Revisit Triggers

- Vector store: revisit if filtering/scale needs exceed Qdrant, or pgvector
  proves sufficient (would simplify the stack).
- Graph: promote NetworkX → Neo4j only if relationship queries become a
  bottleneck (Phase 3+).
- DB: SQLite → Postgres at the cloud/scale boundary.

## Related

[25-adr-log](25-adr-log.md) · [03-system-architecture](03-system-architecture.md) · [05-engineering-principles](05-engineering-principles.md)
