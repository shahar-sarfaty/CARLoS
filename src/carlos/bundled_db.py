from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import importlib.resources as resources

from .database import load_database, PandasCarlosDatabase


_BUNDLED_NAME = "metrics_database.parquet"


def bundled_database_path() -> Path:
    """
    Returns a *real filesystem path* to the packaged parquet file.
    Works even if the package is installed as a wheel/zip via as_file().
    """
    pkg = resources.files("carlos") / "data" / _BUNDLED_NAME
    with resources.as_file(pkg) as p:
        return Path(p)


def load_bundled_database() -> PandasCarlosDatabase:
    """Load the read-only bundled database into memory."""
    return load_database(bundled_database_path())


def copy_bundled_database(dest: str | Path, *, overwrite: bool = False) -> Path:
    """
    Copy the bundled DB to a user-writable location.
    Users should add rows to THIS copy (not inside site-packages).
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and not overwrite:
        return dest

    src = bundled_database_path()
    shutil.copy2(src, dest)
    return dest