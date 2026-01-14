# src/carlos/types.py
from __future__ import annotations

from dataclasses import dataclass, field, replace
import numpy as np
from typing import Any, Mapping, Optional, Sequence

_EMBED_DIM_DEFAULT = 512


@dataclass(frozen=True)
class CarlosVector:
    """
    Concise, prompt-independent behavioral representation of a LoRA.

    - direction: 512-d (by default) vector in embedding space describing the semantic shift
    - strength: scalar magnitude of effect
    - consistency: scalar coherence/stability of the effect
    """

    direction: np.ndarray  # shape: (D,)
    strength: float
    consistency: float

    def __post_init__(self) -> None:
        d = np.asarray(self.direction, dtype=np.float32)
        if d.ndim != 1:
            raise ValueError(f"direction must be 1D, got shape {d.shape}")
        if d.size == 0:
            raise ValueError("direction must be non-empty")
        object.__setattr__(self, "direction", d)

        # Be strict but not annoying: allow any finite floats
        if not np.isfinite(self.strength):
            raise ValueError(f"strength must be finite, got {self.strength}")
        if not np.isfinite(self.consistency):
            raise ValueError(f"consistency must be finite, got {self.consistency}")

    @property
    def dim(self) -> int:
        return int(self.direction.size)

    def to_jsonable(self) -> dict[str, Any]:
        """Safe-ish for parquet/json: direction becomes a plain Python list."""
        return {
            "direction": self.direction.astype(float).tolist(),
            "strength": float(self.strength),
            "consistency": float(self.consistency),
        }

    @classmethod
    def from_direction_strength_consistency(
        cls,
        direction: Sequence[float] | np.ndarray,
        strength: float,
        consistency: float,
        *,
        expected_dim: int | None = _EMBED_DIM_DEFAULT,
    ) -> "CarlosVector":
        d = np.asarray(direction, dtype=np.float32).reshape(-1)
        if expected_dim is not None and d.size != expected_dim:
            raise ValueError(f"Expected direction dim {expected_dim}, got {d.size}")
        return cls(direction=d, strength=float(strength), consistency=float(consistency))


@dataclass(frozen=True)
class IndexingResult:
    """
    Result of indexing a single LoRA into a database.

    lora_id:
      stable identifier inside your system (you can choose: version_id, civit_id, folder_name, etc.)
    vector:
      CARLoS metrics for retrieval.
    row:
      Optional: the exact row dict you inserted into the DB (parquet-ready).
    artifacts:
      Optional non-stable extras (paths, thumbnails, debug logs, etc.)
    """

    lora_id: str
    vector: CarlosVector
    row: Mapping[str, Any]

    # src/carlos/types.py


# ... keep CarlosVector + IndexingResult above as-is ...


@dataclass(frozen=True)
class RetrievalResult:
    """
    Result of retrieving a LoRA from the database.

    This is intentionally row-first: the `row` is the primary payload so callers can
    inspect any metadata columns without another lookup.

    Fields
    ------
    lora_id:
      Stable identifier for the LoRA in your system. In the bundled DB this is
      typically the row's `version_id`, but retrieval backends may choose differently.
    score:
      A higher-is-better score. The absolute scale is not a stable contract.
    row:
      The original row payload (parquet-friendly primitives recommended).
    rank:
      Optional 1-based rank among returned results.
    vector:
      Optional CARLoS vector for this row (helpful for debugging / filters).
    meta:
      Optional extra structured info (e.g., debug signals, query embedding id, etc.).
      Not part of the stable DB schema.
    """

    lora_id: str
    score: float
    row: Mapping[str, Any]
    rank: Optional[int] = None
    vector: Optional["CarlosVector"] = None
    meta: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        s = float(self.score)
        if not np.isfinite(s):
            raise ValueError(f"score must be finite, got {self.score}")
        if self.rank is not None:
            r = int(self.rank)
            if r <= 0:
                raise ValueError(f"rank must be >= 1, got {self.rank}")

    def get(self, key: str, default: Any = None) -> Any:
        """Convenience access to `row` fields."""
        return self.row.get(key, default)

    @property
    def version_id(self) -> Optional[str]:
        """
        Convenience alias for the common DB key column.
        Returns None if the row does not include `version_id`.
        """
        v = self.row.get("version_id")
        return str(v) if v is not None else None

    def with_rank(self, rank: int) -> "RetrievalResult":
        """Return a copy with `rank` set (keeps the dataclass frozen)."""
        return replace(self, rank=int(rank))

    def to_jsonable(self) -> dict[str, Any]:
        """
        Convert to JSON/parquet-friendly primitives.
        Note: `row` is passed through as-is; ensure your DB rows are primitive-friendly.
        """
        return {
            "lora_id": str(self.lora_id),
            "score": float(self.score),
            "rank": int(self.rank) if self.rank is not None else None,
            "row": dict(self.row),
            "vector": self.vector.to_jsonable() if self.vector is not None else None,
            "meta": dict(self.meta) if self.meta is not None else {},
        }

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any],
        *,
        score: float,
        lora_id: Optional[str] = None,
        rank: Optional[int] = None,
        vector: Optional["CarlosVector"] = None,
        meta: Optional[Mapping[str, Any]] = None,
        id_column: str = "version_id",
    ) -> "RetrievalResult":
        """
        Helper constructor for the common case of building results from DB rows.
        """
        _row = dict(row)
        _id = lora_id
        if _id is None:
            if id_column not in _row:
                raise KeyError(f"row missing id_column={id_column!r}")
            _id = str(_row[id_column])
        return cls(
            lora_id=str(_id),
            score=float(score),
            row=_row,
            rank=int(rank) if rank is not None else None,
            vector=vector,
            meta=dict(meta) if meta is not None else {},
        )