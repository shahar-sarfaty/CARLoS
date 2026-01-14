from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional, Mapping, Any

CIVITAI_API_KEY_ENV = "CIVITAI_API_KEY"

def _none_if_blank(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = str(s).strip()
    return s if s else None

@dataclass(frozen=True)
class IndexingConfig:
    # Filesystem / caching
    working_directory: Path = Path("./carlos_working_directory")
    models_cache_dir: Optional[Path] = None

    # CivitAI
    civitai_key_str: Optional[str] = None  # if None, resolve via env at runtime

    # Generation
    base_model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"
    device: str = "cuda"
    torch_dtype: str = "float16"  # keep as string to avoid importing torch here
    num_inference_steps: int = 25
    lora_scale: float = 1.0
    initial_seed: int = 42
    max_batch_size: int = 4

    # Indexing workload
    workload_type: str = "full"  # "full" | "smoke_test" | "mini_test" | "dry_run"
    num_images_per_prompt: int = 16
    thumbnail_size: Optional[tuple[int, int]] = (128, 128)  # None = keep full res

    # Operational
    debug_download: bool = False
    save_downloaded_model: bool = True
    save_generated_images_and_embeddings: bool = True
    save_raw_clip_diffs: bool = True
    save_metrics_as_dataframe: bool = True
    
    def resolved_civitai_key(self) -> Optional[str]:
        return _none_if_blank(self.civitai_key_str) or _none_if_blank(os.getenv(CIVITAI_API_KEY_ENV))

    def with_overrides(self, **kwargs: Any) -> "IndexingConfig":
        # ergonomic: cfg = cfg.with_overrides(num_images_per_prompt=2)
        return replace(self, **{k: v for k, v in kwargs.items() if v is not None})

@dataclass(frozen=True)
class RetrievalConfig:
    # Filesystem / caching
    working_directory: Path = Path("./carlos_working_directory")
    models_cache_dir: Optional[Path] = working_directory / "models_cache"
    device: str = "cuda"

    def with_overrides(self, **kwargs: Any) -> "RetrievalConfig":
        # ergonomic: cfg = cfg.with_overrides(num_images_per_prompt=2)
        return replace(self, **{k: v for k, v in kwargs.items() if v is not None})