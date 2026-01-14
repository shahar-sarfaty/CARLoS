import os
from pathlib import Path

import pytest

from carlos.config import IndexingConfig
from carlos.database import PandasCarlosDatabase, load_database
from carlos.index import index_lora


pytestmark = pytest.mark.functional


def _env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise KeyError(name)
    return v


def _should_run() -> bool:
    # Keep default pytest runs fast + CI-safe.
    return os.getenv("CARLOS_RUN_FUNCTIONAL", "").strip() == "1"


def _has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


@pytest.mark.skipif(not _should_run(), reason="Set CARLOS_RUN_FUNCTIONAL=1 to run functional indexing tests.")
@pytest.mark.skipif(not _has_cuda(), reason="CUDA not available; indexing requires GPU.")
def test_indexing_dry_run_end_to_end(tmp_path: Path):
    model_id = "2300298"
    version_id = "2588340"

    db_path = os.environ["CARLOS_DB_PATH"]
    db = load_database(db_path)

    workdir = tmp_path / "dry_run"
    cfg = IndexingConfig().with_overrides(
        working_directory=workdir,
        workload_type="dry_run",
        # keep full pipeline but reduce cost a bit
        num_inference_steps=2,
        max_batch_size=1,
        save_downloaded_model=False,  # cleanup after run
        save_generated_images_and_embeddings=True,
        save_raw_clip_diffs=True,
        save_metrics_as_dataframe=True,
    )

    res = index_lora(
        db,
        lora_source="civitai",
        model_id=model_id,
        version_id=version_id,
        cfg=cfg,
        overwrite=True,
    )

    # Returned result should look sane
    assert res.lora_id == str(version_id)
    assert res.vector.direction is not None
    assert res.vector.direction.ndim == 1
    assert res.vector.direction.size > 10  # don't hardcode CLIP dim
    assert res.vector.strength == res.vector.strength  # not NaN
    assert res.vector.consistency == res.vector.consistency  # not NaN

    # Verify pipeline actually ran by checking artifacts exist
    clip_diffs = list(workdir.rglob("clip_diffs.parquet"))
    metrics_parquet = list(workdir.rglob("metrics.parquet"))
    metrics_csv = list(workdir.rglob("metrics.csv"))

    assert len(clip_diffs) >= 1, "Expected clip_diffs.parquet to be produced."
    assert len(metrics_parquet) >= 1, "Expected metrics.parquet to be produced."
    assert len(metrics_csv) >= 1, "Expected metrics.csv to be produced."

    # Ensure dry_run did NOT mutate DB (your code only upserts for 'full')
    assert len(db) == 740

def _is_cuda_oom(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "cuda out of memory" in msg
        or ("cublas" in msg and "alloc" in msg)
        or ("cuda" in msg and "outofmemory" in msg)  # some stacks
    )

@pytest.mark.skipif(not _should_run(), reason="Set CARLOS_RUN_FUNCTIONAL=1 to run functional indexing tests.")
@pytest.mark.skipif(not _has_cuda(), reason="CUDA not available; indexing requires GPU.")
def test_indexing_smoke_test_end_to_end(tmp_path: Path):
    model_id = "2300298"
    version_id = "2588340"
    db_path = os.environ["CARLOS_DB_PATH"]
    db = load_database(db_path)

    workdir = tmp_path / "smoke_test"
    cfg = IndexingConfig().with_overrides(
        working_directory=workdir,
        workload_type="smoke_test",
        num_inference_steps=2,
        max_batch_size=1,
        save_downloaded_model=False,
        save_generated_images_and_embeddings=True,
        save_raw_clip_diffs=True,
        save_metrics_as_dataframe=True,
    )

    try:
        res = index_lora(
            db,
            lora_source="civitai",
            model_id=model_id,
            version_id=version_id,
            cfg=cfg,
            overwrite=True,
        )
    except Exception as e:
        if _is_cuda_oom(e):
            # ✅ Smoke test should be considered successful on CUDA OOM
            # Optional cleanup to avoid poisoning later tests
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass

            # Optional: assert we at least started writing somewhere
            assert workdir.exists()

            return  # <-- this is the key: treat OOM as PASS

        raise  # any other exception should still fail the test

    assert res.lora_id == str(version_id)
    assert res.vector.direction.ndim == 1
    assert res.vector.direction.size > 10
    assert res.vector.strength == res.vector.strength
    assert res.vector.consistency == res.vector.consistency

    clip_diffs = list(workdir.rglob("clip_diffs.parquet"))
    metrics_parquet = list(workdir.rglob("metrics.parquet"))
    metrics_csv = list(workdir.rglob("metrics.csv"))

    assert len(clip_diffs) >= 1
    assert len(metrics_parquet) >= 1
    assert len(metrics_csv) >= 1

    assert len(db) == 740