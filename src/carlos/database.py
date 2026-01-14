# src/carlos/database.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from .types import CarlosVector, IndexingResult

# Aligned with your create_metrics_dataframe() intent in index.py
DEFAULT_REQUIRED_COLUMNS: tuple[str, ...] = (
    "version_id",
    "model_id",
    "model_name",
    "folder_name",
    "model_description",
    "model_download_count",
    "model_nsfw_level",
    "direction",
    "strength",
    "consistency",
)

def _coerce_int64(value: Any, *, field: str) -> int:
    if value is None:
        raise ValueError(f"{field} cannot be None")
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            raise ValueError(f"{field} cannot be empty string")
        return int(s)
    # allow pandas scalars
    try:
        return int(value)
    except Exception as e:
        raise TypeError(f"Could not coerce {field}={value!r} to int") from e


def _coerce_optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return int(value)

def _direction_to_storage(direction: np.ndarray) -> list[float]:
    """
    Lossless for float32-origin vectors:
      float32 -> python float (float64) is exact, and can be cast back to float32 exactly.
    """
    d = np.asarray(direction).reshape(-1)
    if d.size == 0:
        raise ValueError("direction must be non-empty")
    # Force float32 canonical representation before storing.
    d32 = d.astype(np.float32, copy=False)
    # Convert each float32 to python float (exact), for parquet friendliness.
    return [float(x) for x in d32.tolist()]


def _direction_from_storage(obj: Any) -> np.ndarray:
    if isinstance(obj, np.ndarray):
        return obj.astype(np.float32).reshape(-1)
    if isinstance(obj, (list, tuple)):
        # Cast back to float32; if values came from float32 originally, this is exact.
        return np.asarray(obj, dtype=np.float32).reshape(-1)
    raise TypeError(f"Unsupported direction storage type: {type(obj)}")


class CarlosDatabase:
    """
    Minimal DB interface. Keep it small and stable.

    Implementations should be able to:
      - expose a pandas DataFrame view
      - upsert indexing results
      - retrieve stored vectors for retrieval
      - save/load
    """

    def to_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.to_dataframe())

    def required_columns(self) -> Sequence[str]:
        raise NotImplementedError

    def upsert_row(self, row: Mapping[str, Any]) -> None:
        raise NotImplementedError

    def upsert_indexing_result(self, result: IndexingResult) -> None:
        self.upsert_row(self.row_from_indexing_result(result))

    def row_from_indexing_result(self, result: IndexingResult) -> Dict[str, Any]:
        # Default behavior: store core metrics + whatever else caller included in result.row
        base = dict(result.row or {})
        base["direction"] = _direction_to_storage(result.vector.direction)
        base["strength"] = float(result.vector.strength)
        base["consistency"] = float(result.vector.consistency)
        return base

    def get_vector(self, *, key: str, value: Any) -> CarlosVector:
        df = self.to_dataframe()
        if key not in df.columns:
            raise KeyError(f"Unknown key column: {key}")
        hits = df[df[key] == value]
        if hits.empty:
            raise KeyError(f"No row found where {key}={value!r}")
        row = hits.iloc[0].to_dict()
        return CarlosVector(
            direction=_direction_from_storage(row["direction"]),
            strength=float(row["strength"]),
            consistency=float(row["consistency"]),
        )

    def iter_vectors(self) -> Iterable[tuple[dict[str, Any], CarlosVector]]:
        df = self.to_dataframe()
        for _, r in df.iterrows():
            row = r.to_dict()
            vec = CarlosVector(
                direction=_direction_from_storage(row["direction"]),
                strength=float(row["strength"]),
                consistency=float(row["consistency"]),
            )
            yield row, vec

    def save_parquet(self, path: str | Path) -> None:
        raise NotImplementedError


@dataclass
class PandasCarlosDatabase(CarlosDatabase):
    """
    Parquet-backed DB wrapper over a pandas DataFrame.

    By default, identifies rows by `version_id` when upserting.
    """

    df: pd.DataFrame
    path: Optional[Path] = None
    key_column: str = "version_id"
    _required_columns: Sequence[str] = DEFAULT_REQUIRED_COLUMNS

    def __post_init__(self) -> None:
        # Make a defensive copy to avoid spooky mutations.
        self.df = self.df.copy()

        # Ensure required columns exist (create if missing).
        for c in self._required_columns:
            if c not in self.df.columns:
                self.df[c] = None

        # Basic sanity for core numeric cols
        for c in ("strength", "consistency"):
            if c in self.df.columns:
                # don't force dtype conversion here; just ensure column exists
                pass

    def required_columns(self) -> Sequence[str]:
        return tuple(self._required_columns)

    def to_dataframe(self) -> pd.DataFrame:
        return self.df

    def upsert_row(self, row: Mapping[str, Any]) -> None:
        if self.key_column not in row:
            raise KeyError(
                f"Row must include key column {self.key_column!r}. "
                f"Got keys: {sorted(row.keys())}"
            )

        # Validate required fields exist (can be None, but must be present)
        for c in self._required_columns:
            if c not in row:
                raise KeyError(f"Row missing required column {c!r}")

        key_val = row[self.key_column]

        row = dict(row)

        # Enforce canonical types for stable parquet schema
        row["version_id"] = _coerce_int64(row.get("version_id"), field="version_id")
        row["model_id"] = _coerce_optional_int(row.get("model_id"))
        row["model_nsfw_level"] = _coerce_optional_int(row.get("model_nsfw_level"))
        row["model_download_count"] = _coerce_optional_int(row.get("model_download_count"))

        # Strength/consistency should be floats (allow None -> NaN)
        if "strength" in row and row["strength"] is not None:
            row["strength"] = float(row["strength"])
        if "consistency" in row and row["consistency"] is not None:
            row["consistency"] = float(row["consistency"])
    
        # Normalize direction for storage
        direction_obj = row.get("direction", None)
        if direction_obj is not None:
            row = dict(row)
            row["direction"] = (
                _direction_to_storage(_direction_from_storage(direction_obj))
                if not isinstance(direction_obj, list)
                else direction_obj
            )

        df = self.df
        mask = df[self.key_column] == key_val
        hit_indices = df.index[mask].tolist()

        if len(hit_indices) > 1:
            raise ValueError(
                f"Database corruption: multiple rows with {self.key_column}={key_val!r} "
                f"({len(hit_indices)} rows)."
            )

        if len(hit_indices) == 1:
            idx = hit_indices[0]
            for k, v in row.items():
                df.at[idx, k] = v
        else:
            row_df = pd.DataFrame([dict(row)])
            if self.df.empty:
                # Initialize dataframe with correct dtypes
                self.df = row_df.astype(row_df.dtypes.to_dict())
            else:
                self.df.loc[len(self.df)] = row_df.iloc[0]

    def save_parquet(self, path: str | Path | None = None) -> Path:
        out = Path(path) if path is not None else self.path
        if out is None:
            raise ValueError("No output path provided. Pass `path=...` or set db.path.")
        out.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_parquet(out, index=False)
        self.path = out
        return out


def load_database(source: str | Path) -> PandasCarlosDatabase:
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Database path does not exist: {path}")
    if path.suffix.lower() != ".parquet":
        raise ValueError(f"Expected a .parquet file, got: {path.name}")

    df = pd.read_parquet(path)
    return PandasCarlosDatabase(df=df, path=path)