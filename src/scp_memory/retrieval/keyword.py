"""Keyword relevance — pure Okapi BM25 over a candidate corpus (13-retrieval-model).

Lexical scoring complements semantic vectors: it is precise on exact terms,
identifiers, and rare tokens. BM25 is computed over the metadata-filtered
candidate set, with idf derived from that set. At MVP scale this is an O(N) pass
per query; the production scale path is an inverted index (SQLite FTS5 / Postgres
tsvector) or the vector backend's native keyword support.
"""

import math
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class BM25Params:
    k1: float = 1.5
    b: float = 0.75


_DEFAULT_PARAMS = BM25Params()


def bm25_scores(
    query_tokens: list[str],
    documents: list[list[str]],
    params: BM25Params = _DEFAULT_PARAMS,
) -> list[float]:
    """Return a BM25 score per document (aligned with ``documents``).

    ``documents`` is a list of token lists. Scores are >= 0; higher is more
    relevant. An empty query or corpus yields all-zero scores.
    """
    n = len(documents)
    if n == 0 or not query_tokens:
        return [0.0] * n

    lengths = [len(d) for d in documents]
    avgdl = (sum(lengths) / n) or 1.0
    terms = set(query_tokens)

    counters = [Counter(d) for d in documents]
    df = {t: sum(1 for c in counters if t in c) for t in terms}
    idf = {t: math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) for t in terms}

    scores: list[float] = []
    for counter, dl in zip(counters, lengths, strict=True):
        score = 0.0
        for t in terms:
            freq = counter.get(t, 0)
            if freq == 0:
                continue
            denom = freq + params.k1 * (1 - params.b + params.b * dl / avgdl)
            score += idf[t] * (freq * (params.k1 + 1)) / denom
        scores.append(score)
    return scores
