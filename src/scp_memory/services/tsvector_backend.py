"""PostgreSQL tsvector keyword backend — inverted-index scale path (13-retrieval-model).

The Postgres analogue of the FTS5 backend: a ``STORED GENERATED`` ``tsvector``
column over ``memories.content`` with a GIN index does full-text matching and
``ts_rank`` ranking in the database. The generated column stays in sync
automatically on every write — no application write-path changes.

Integration-only: selected via ``SCP_KEYWORD_BACKEND=tsvector`` and exercised
against a real PostgreSQL instance in CI. Fails loud on a non-PostgreSQL engine.
"""

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from scp_memory.models.memory import Memory

logger = logging.getLogger("scp_memory.retrieval.keyword.tsvector")

_REGCONFIG = "english"


class TsvectorBackend:
    """GIN-indexed ``tsvector`` over ``memories.content``, namespace-scoped at query."""

    name = "tsvector"

    def _ensure(self, db: Session) -> None:
        """Add the generated tsvector column + GIN index once (idempotent)."""
        if db.bind is None or db.bind.dialect.name != "postgresql":
            raise RuntimeError(
                f"SCP_KEYWORD_BACKEND=tsvector requires a PostgreSQL engine, got "
                f"'{getattr(db.bind, 'dialect', None)}'. Use 'fts5' for SQLite."
            )
        has_column = db.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='memories' AND column_name='content_tsv'"
            )
        ).first()
        if has_column:
            return
        db.execute(
            text(
                "ALTER TABLE memories ADD COLUMN content_tsv tsvector "
                f"GENERATED ALWAYS AS (to_tsvector('{_REGCONFIG}', content)) STORED"
            )
        )
        db.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_memories_content_tsv "
                "ON memories USING GIN (content_tsv)"
            )
        )
        db.commit()
        logger.info("tsvector column + GIN index created")

    def scores(
        self,
        *,
        db: Session,
        query: str,
        namespace: str,
        type_: str | None,
        candidates: list[Memory],
    ) -> dict[str, float]:
        self._ensure(db)
        sql = text(
            f"SELECT id, ts_rank(content_tsv, plainto_tsquery('{_REGCONFIG}', :q)) AS rank "
            "FROM memories "
            f"WHERE namespace = :ns AND content_tsv @@ plainto_tsquery('{_REGCONFIG}', :q)"
        )
        rows = db.execute(sql, {"q": query, "ns": namespace}).all()
        candidate_ids = {m.id for m in candidates}
        return {row.id: float(row.rank) for row in rows if row.id in candidate_ids}
