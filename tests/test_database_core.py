import numpy as np
import pandas as pd
import pytest

from carlos.database import (
    DEFAULT_REQUIRED_COLUMNS,
    PandasCarlosDatabase,
    load_database,
)
from carlos.types import CarlosVector, IndexingResult


def _min_row(version_id: int, *, direction=None, strength=1.0, consistency=0.5):
    # Keep required columns present to satisfy upsert validation.
    d = np.asarray(direction if direction is not None else [1.0, 0.0, 0.0], dtype=np.float32)
    return {
        "version_id": version_id,
        "model_id": 111,
        "model_name": "Model",
        "folder_name": f"folder_{version_id}",
        "model_description": "desc",
        "model_download_count": 10,
        "model_nsfw_level": 0,
        "direction": d,  # db will normalize to list[float] storage
        "strength": strength,
        "consistency": consistency,
    }


def test_upsert_and_get_vector_roundtrip_types():
    df = pd.DataFrame(columns=list(DEFAULT_REQUIRED_COLUMNS))
    db = PandasCarlosDatabase(df=df)

    row = _min_row("123")  # str should be coerced to int
    db.upsert_row(row)

    out = db.to_dataframe()
    assert len(out) == 1
    assert int(out.loc[0, "version_id"]) == 123
    assert int(out.loc[0, "model_id"]) == 111

    # Direction should be stored as list-friendly type
    stored_dir = out.loc[0, "direction"]
    assert isinstance(stored_dir, (list, tuple, np.ndarray))

    vec = db.get_vector(key="version_id", value=123)
    assert isinstance(vec, CarlosVector)
    assert vec.direction.dtype == np.float32
    assert vec.direction.ndim == 1
    assert np.allclose(vec.direction, np.array([1.0, 0.0, 0.0], dtype=np.float32))
    assert vec.strength == pytest.approx(1.0)
    assert vec.consistency == pytest.approx(0.5)


def test_upsert_updates_existing_row_not_duplicate():
    df = pd.DataFrame(columns=list(DEFAULT_REQUIRED_COLUMNS))
    db = PandasCarlosDatabase(df=df)

    db.upsert_row(_min_row(1, strength=1.0))
    db.upsert_row(_min_row(1, strength=2.0))  # same version_id => update

    out = db.to_dataframe()
    assert len(out) == 1
    assert float(out.loc[0, "strength"]) == pytest.approx(2.0)


def test_upsert_detects_duplicate_keys_corruption():
    # Simulate a corrupt parquet with duplicate version_id rows.
    df = pd.DataFrame([_min_row(7), _min_row(7)])
    db = PandasCarlosDatabase(df=df)

    with pytest.raises(ValueError, match="multiple rows"):
        db.upsert_row(_min_row(7, strength=3.0))


def test_save_and_load_database_parquet(tmp_path):
    df = pd.DataFrame([_min_row(10), _min_row(20, direction=[0, 1, 0])])
    db = PandasCarlosDatabase(df=df)

    p = tmp_path / "db.parquet"
    db.save_parquet(p)

    db2 = load_database(p)
    assert isinstance(db2, PandasCarlosDatabase)
    assert len(db2) == 2

    v10 = db2.get_vector(key="version_id", value=10)
    v20 = db2.get_vector(key="version_id", value=20)
    assert np.allclose(v10.direction, np.array([1, 0, 0], dtype=np.float32))
    assert np.allclose(v20.direction, np.array([0, 1, 0], dtype=np.float32))


def test_upsert_indexing_result_inserts_vector_fields():
    df = pd.DataFrame(columns=list(DEFAULT_REQUIRED_COLUMNS))
    db = PandasCarlosDatabase(df=df)

    vec = CarlosVector.from_direction_strength_consistency([0.0, 0.0, 1.0], 3.0, 0.9, expected_dim=3)
    res = IndexingResult(
        lora_id="x",
        vector=vec,
        row={
            # required columns:
            "version_id": 55,
            "model_id": 5,
            "model_name": "M",
            "folder_name": "F",
            "model_description": "D",
            "model_download_count": 1,
            "model_nsfw_level": 0,
            # these will be overwritten from vector by row_from_indexing_result:
            "direction": [999],
            "strength": -1,
            "consistency": -1,
        },
    )

    db.upsert_indexing_result(res)
    got = db.get_vector(key="version_id", value=55)
    assert np.allclose(got.direction, np.array([0, 0, 1], dtype=np.float32))
    assert got.strength == pytest.approx(3.0)
    assert got.consistency == pytest.approx(0.9)