# src/carlos/__init__.py
"""
CARLoS: Concise Assessment Representation of LoRAs at Scale.

Public API principles:
- Stable, minimal entry points for loading a database, retrieving LoRAs, and
  indexing new LoRAs.
- Internal implementation details (generation, embeddings, storage layout) are
  not part of the public contract and may change between versions.
"""

from ._version import __version__
from .database import CarlosDatabase, load_database
from .types import CarlosVector, IndexingResult, RetrievalResult
from .bundled_db import copy_bundled_database, load_bundled_database

__all__ = [
    "__version__",
    "CarlosDatabase",
    "CarlosVector",
    "IndexingResult",
    "RetrievalResult",
    "load_database",
    "load_bundled_database",
    "copy_bundled_database",
    "index_lora",
    "retrieve",
]
# Lazy import: indexing pulls heavy GPU-only dependencies
def index_lora(*args, **kwargs):
    from .index import index_lora as _index_lora
    return _index_lora(*args, **kwargs)

def retrieve(*args, **kwargs):
    from .retrieve import retrieve as _retrieve
    return _retrieve(*args, **kwargs)