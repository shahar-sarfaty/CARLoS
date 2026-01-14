# src/carlos/_optional.py
from __future__ import annotations
from importlib import import_module
from typing import Any

class OptionalDependencyError(ModuleNotFoundError):
    pass

def require(module: str) -> Any:
    try:
        return import_module(module)
    except ModuleNotFoundError as e:
        raise OptionalDependencyError(
            f"Optional dependency '{module}' is required for this operation but is not installed. "
            "Install it in your environment (recommended: via conda for GPU stacks)."
        ) from e