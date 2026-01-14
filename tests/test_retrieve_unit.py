import importlib
import pytest
import pandas as pd
import numpy as np

from carlos.database import DEFAULT_REQUIRED_COLUMNS, PandasCarlosDatabase


def _row(version_id: int, direction, strength, consistency):
    return {
        "version_id": version_id,
        "model_id": 1,
        "model_name": "M",
        "folder_name": f"F{version_id}",
        "model_description": "D",
        "model_download_count": 1,
        "model_nsfw_level": 0,
        "direction": np.asarray(direction, dtype=np.float32),
        "strength": float(strength),
        "consistency": float(consistency),
    }


def test_retrieve_filters_and_ranks_with_stubs(monkeypatch):
    torch = pytest.importorskip("torch")

    # IMPORTANT: force module import (avoid package-level `retrieve` symbol)
    r = importlib.import_module("carlos.retrieve")

    df = pd.DataFrame(
        [
            _row(1, [1, 0, 0], strength=1.0, consistency=0.9),
            _row(2, [0, 1, 0], strength=1.0, consistency=0.9),
            _row(3, [0, 0, 1], strength=99.0, consistency=0.9),  # filtered by strength
            _row(4, [1, 1, 0], strength=1.0, consistency=0.0),   # filtered by consistency
        ],
        columns=list(DEFAULT_REQUIRED_COLUMNS),
    )
    db = PandasCarlosDatabase(df=df)

    # Stub query repr and scoring deterministically (avoid CLIP/model loads)
    monkeypatch.setattr(r, "_embed_query_stub", lambda query, cfg: torch.tensor([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        r,
        "_score_stub",
        lambda query_repr, vec, row: float(np.dot(vec.direction, query_repr.numpy())),
    )

    out = r.retrieve(
        db,
        "whatever",
        top_k=10,
        max_strength=9.8,
        min_consistency=0.041,
    )

    # Only rows 1 and 2 remain; score = dot(direction, [1,0,0]) => row1 wins
    assert [x.version_id for x in out] == ["1", "2"]
    assert [x.rank for x in out] == [1, 2]
    assert out[0].score > out[1].score


def test_retrieve_validates_inputs():
    pytest.importorskip("torch")
    r = importlib.import_module("carlos.retrieve")

    df = pd.DataFrame(columns=list(DEFAULT_REQUIRED_COLUMNS))
    db = PandasCarlosDatabase(df=df)

    with pytest.raises(ValueError):
        r.retrieve(db, "", top_k=5)

    with pytest.raises(ValueError):
        r.retrieve(db, "ok", top_k=0)