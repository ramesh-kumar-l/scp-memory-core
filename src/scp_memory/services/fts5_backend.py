"""SQLite FTS5 keyword backend — the inverted-index scale path (13-retrieval-model).

Replaces the O(N) in-process BM25 pass with a persistent FTS5 inverted index that
does the matching and ranking inside SQLite. The index is *external-content*
(``content='memories'``) so it stores only the postings, not a copy of the text,
and is kept in sync by AFTER INSERT/UPDATE/DELETE triggers — no application write
path changes. ``bm25()`` provides Okapi ranking over the whole indexed corpus.

Integration-only: selected via ``SCP_KEYWORD_BACKEND=fts5`` and requires SQLite
built with FTS5 (standard in modern CPython). Fails loud on a non-SQLite engine.
"""

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from scp_memory.intelligence.similarity import tokenize
from scp_memory.models.memory import Memory

logger = logging.getLogger("scp_memory.retrieval.keyword.fts5")

_TRIGGERS = (
    """CREATE TRIGGER IF NOT EXISTS memories_fts_ai AFTER INSERT ON memories BEGIN
        INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
    END;""",
    """CREATE TRIGGER IF NOT EXISTS memories_fts_ad AFTER DELETE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
    END;""",
    """CREATE TRIGGER IF NOT EXISTS memories_fts_au AFTER UPDATE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
        INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
    END;""",
)


class Fts5Backend:
    """FTS5 inverted index over ``memories.content``, namespace-scoped at query time."""

    name = "fts5"

    def _ensure(self, db: Session) -> None:
        """Create the FTS5 table + sync triggers and backfill once (idempotent)."""
        if db.bind is None or db.bind.dialect.name != "sqlite":
            raise RuntimeError(
                f"SCP_KEYWORD_BACKEND=fts5 requires a SQLite engine, got "
                f"'{getattr(db.bind, 'dialect', None)}'. Use 'tsvector' for PostgreSQL."
            )
        exists = db.execute(
            text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='memories_fts'")
        ).first()
        if exists:
            return
        db.execute(
            text(
                "CREATE VIRTUAL TABLE memories_fts USING fts5("
                "content, content='memories', content_rowid='rowid')"
            )
        )
        for trigger in _TRIGGERS:
            db.execute(text(trigger))
        db.execute(text("INSERT INTO memories_fts(memories_fts) VALUES ('rebuild')"))
        db.commit()
        logger.info("fts5 index created and backfilled")

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
        tokens = list(tokenize(query))
        if not tokens:
            return {}
        # OR the query tokens; quote each so punctuation can't break FTS5 syntax.
        match = " OR ".join(f'"{t}"' for t in tokens)
        sql = text(
            "SELECT m.id AS id, bm25(memories_fts) AS rank "
            "FROM memories_fts JOIN memories m ON m.rowid = memories_fts.rowid "
            "WHERE memories_fts MATCH :match AND m.namespace = :ns"
        )
        rows = db.execute(sql, {"match": match, "ns": namespace}).all()
        candidate_ids = {m.id for m in candidates}
        # bm25() is a cost (more relevant = more negative); negate for higher-is-better.
        return {row.id: -float(row.rank) for row in rows if row.id in candidate_ids}
