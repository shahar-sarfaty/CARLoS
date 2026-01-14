import os
import pytest

from carlos.database import load_database
from carlos.retrieve import retrieve


pytestmark = pytest.mark.functional


def _should_run():
    # Opt-in, so CI doesn't explode
    return os.getenv("CARLOS_RUN_FUNCTIONAL", "") == "1"


@pytest.mark.skipif(not _should_run(), reason="Set CARLOS_RUN_FUNCTIONAL=1 to run functional retrieval tests.")
def test_real_retrieve_is_query_sensitive():
    # Use bundled DB or point to a known parquet in your repo/dev env.
    # Option A: bundled (preferred if you ship one)
    # db = load_database()  # if your API supports it
    #
    # Option B: env var points at a local parquet
    db_path = os.environ["CARLOS_DB_PATH"]
    db = load_database(db_path)

    queries = [
        "anime portrait, soft lighting",
        "neon city at night, long exposure",
        "snowfall, winter clothing, cold palette",
        "oil painting brush strokes",
    ]

    outputs = []
    for q in queries:
        res = retrieve(db, q, top_k=10)
        assert len(res) > 0
        # basic health checks
        assert all(r.score == r.score for r in res)  # not NaN
        assert len({r.version_id for r in res}) == len(res)  # no duplicates
        outputs.append(tuple(r.version_id for r in res[:5]))

    # “real functionality” sanity: not all queries produce identical top-5
    assert len(set(outputs)) >= 2, f"Degenerate retrieval: all queries returned same top-5: {outputs}"


@pytest.mark.skipif(not _should_run(), reason="Set CARLOS_RUN_FUNCTIONAL=1 to run functional retrieval tests.")
def test_real_retrieve_is_repeatable_for_same_query():
    db_path = os.environ["CARLOS_DB_PATH"]
    db = load_database(db_path)

    q = "neon city at night, long exposure"
    r1 = retrieve(db, q, top_k=10)
    r2 = retrieve(db, q, top_k=10)

    assert [x.version_id for x in r1] == [x.version_id for x in r2]
    assert [x.score for x in r1] == [x.score for x in r2]