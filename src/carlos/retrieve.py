# src/carlos/retrieve.py
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple
import numpy as np
import threading
from transformers import CLIPProcessor, CLIPModel
import torch
import time

from .database import CarlosDatabase
from .types import CarlosVector, RetrievalResult
from .generative_prompts import prompts_for_retrieval
from .config import RetrievalConfig

_CLIP_CACHE: Dict[Tuple[str, str], Tuple[CLIPModel, CLIPProcessor]] = {}
_CLIP_CACHE_LOCK = threading.Lock()

def retrieve(
    db: CarlosDatabase,
    query: str,
    *,
    top_k: int = 5,
    max_strength: float = 9.8,
    min_consistency: float = 0.041,
    cfg: RetrievalConfig = RetrievalConfig(),
    ) -> List[RetrievalResult]:
    """
    Retrieve top-k LoRAs from the database that best match `query`.

    This file intentionally provides infrastructure only:
      - filtering
      - result construction
      - ranking / top-k selection

    Embedding + similarity are stubs and must be implemented later.

    Parameters
    ----------
    db:
      Loaded CARLoS database.
    query:
      Free-text user query.
    top_k:
      Maximum number of results to return (<= number of candidates).
    max_strength:
      Filter out rows with strength > max_strength (if provided).
    min_consistency:
      Filter out rows with consistency < min_consistency (if provided).

    Returns
    -------
    List[RetrievalResult]
      Sorted by descending score, with rank set to 1..N.

    Notes
    -----
    Scoring is currently a stub and will raise NotImplementedError.
    """
    if not isinstance(query, str) or query.strip() == "":
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        raise ValueError(f"top_k must be > 0, got {top_k}")

    candidates = list(_iter_candidates(db, max_strength=max_strength, min_consistency=min_consistency))
    if not candidates:
        return []

    if "cuda" in cfg.device and not torch.cuda.is_available():
        print("Warning: CUDA device requested but not available; falling back to CPU.")
        cfg = cfg.with_overrides(device="cpu")

    # ---- Scoring stub (to be replaced by your actual embedding + similarity) ----
    query_repr = _embed_query_stub(query, cfg=cfg)

    scored: List[Tuple[float, Dict[str, Any], CarlosVector]] = []
    for row, vec in candidates:
        score = _score_stub(query_repr, vec, row=row)
        scored.append((float(score), row, vec))

    # Sort: high score first. Keep deterministic tie-breaking by lora_id (version_id).
    scored.sort(key=lambda t: (-t[0], str(t[1].get("version_id", ""))))

    # Top-k and build RetrievalResult with ranks
    out: List[RetrievalResult] = []
    for i, (score, row, vec) in enumerate(scored[:top_k], start=1):
        out.append(
            RetrievalResult.from_row(
                row,
                score=score,
                rank=i,
                vector=vec,
                id_column="version_id",
            )
        )
    return out

def _iter_candidates(
    db: CarlosDatabase,
    *,
    max_strength: float,
    min_consistency: float,
    ) -> Iterable[tuple[Dict[str, Any], CarlosVector]]:
    """
    Yield (row, CarlosVector) pairs satisfying the constraints.
    """
    for row, vec in db.iter_vectors():
        # Defensive: tolerate missing fields in row; vec should be authoritative.
        strength = float(vec.strength)
        consistency = float(vec.consistency)

        if strength > float(max_strength):
            continue
        if consistency < float(min_consistency):
            continue

        # Ensure row is mutable plain dict for result serialization
        yield dict(row), vec

def _load_clip_model(models_cache_dir=None, device="cuda", max_retries=5, wait_seconds=10):
    model_name = "openai/clip-vit-base-patch32"  # You can replace with another CLIP model
    cache_dir_key = models_cache_dir or ""
    cache_key = (cache_dir_key, device)
    
    # Fast path: cached
    with _CLIP_CACHE_LOCK:
        cached = _CLIP_CACHE.get(cache_key)
        if cached is not None:
            return cached
    
    if device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError(
            f"Requested device='{device}' but torch.cuda.is_available() is False. "
            "Install a CUDA-enabled PyTorch build (via conda) and ensure an NVIDIA GPU is available."
        )

    for i in range(max_retries):
        try:
            model = CLIPModel.from_pretrained(model_name, cache_dir=models_cache_dir).to(device)
            success = True
            break
        except:
            print("Retrying to load CLIP model...")
            time.sleep(wait_seconds)
            success = False
    if not success:
            raise RuntimeError(f"Failed to load CLIP model from {model_name} after multiple attempts.")
            
    for i in range(max_retries):
        try:
            processor = CLIPProcessor.from_pretrained(model_name, cache_dir=models_cache_dir)
            success = True
            break
        except:
            print("Retrying to load CLIP processor...")
            time.sleep(wait_seconds)
            success = False
    if not success:
            raise RuntimeError(f"Failed to load CLIP processor from {model_name} after multiple attempts.")
            
    # Store in cache (double-checked under lock)
    with _CLIP_CACHE_LOCK:
        existing = _CLIP_CACHE.get(cache_key)
        if existing is not None:
            return existing
        _CLIP_CACHE[cache_key] = (model, processor)
        return model, processor

def _get_text_embeddings(texts: List[str], model: CLIPModel, processor: CLIPProcessor, device: str) -> torch.Tensor:
    """
    Returns a tensor of shape [N, D] on CPU.
    """
    inputs = processor(
        text=texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    model.eval()
    with torch.no_grad():
        feats = model.get_text_features(**inputs)  # [N, D] on device

    return feats.detach().to("cpu")

def _embed_query_stub(query: str, cfg: RetrievalConfig) -> torch.Tensor:
    """
    Stub: turn a text query into whatever representation your scorer uses.
    Replace with your actual text->embedding pipeline.
    """
    prompts = prompts_for_retrieval()
    model, processor = _load_clip_model(models_cache_dir=cfg.models_cache_dir, device=cfg.device)

    # Decide device (prefer cfg.device if you have it; otherwise keep old behavior)
    device = getattr(cfg, "device", "cuda")
    model = model.to(device)

    prompts_flatten_list: List[str] = []
    for category in prompts:
        for sub_category in prompts[category]:
            for prompt in prompts[category][sub_category]:
                prompts_flatten_list.append(prompt)

    prompts_with_additive_suffix = [p + " " + query for p in prompts_flatten_list]

    # Batch embed (2 batches total instead of 2*N calls)
    raw_embeddings = _get_text_embeddings(prompts_flatten_list, model, processor, device=device)              # [N, D]
    with_suffix_embeddings = _get_text_embeddings(prompts_with_additive_suffix, model, processor, device=device)  # [N, D]

    diffs = with_suffix_embeddings - raw_embeddings  # [N, D]
    average_diff = diffs.mean(dim=0)                 # [D]
    return average_diff.flatten()

def _score_stub(query_repr: torch.Tensor, vec: CarlosVector, *, row: Mapping[str, Any]) -> float:
    """
    Stub: compute similarity between the query representation and a CARLoS vector.
    Replace with your actual scoring logic (e.g., cosine between query direction and vec.direction,
    weighted by strength/consistency, etc).
    """
    lora_direction = torch.tensor(vec.direction)
    return float(torch.cosine_similarity(lora_direction, query_repr, dim=0).item())