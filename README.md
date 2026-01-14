# CARLoS — CLIP-based LoRA Retrieval & Indexing

## 🚀 Quick Start

```bash
# 1. Create environment
conda create -n carlos python=3.9.16 -y
conda activate carlos

# 2. Install PyTorch with CUDA 12.6 and a requirements file
python -m pip install --extra-index-url https://download.pytorch.org/whl/cu126 -r requirements-cu126.lock.txt

# 3. Install CARLoS
pip install carlos
```

```python
import carlos

# Load a writable copy of the bundled database
carlos.copy_bundled_database("metrics.parquet", overwrite=False)
db = carlos.load_database("metrics.parquet")

# Run a retrieval query
results = carlos.retrieve(db, "snowfall, cold winter scene", top_k=5)
for r in results:
    print(r.rank, r.lora_id, r.score)
```

---

## Overview

**CARLoS** is a GPU-backed retrieval and indexing library for Stable Diffusion LoRA modules.

It supports two distinct workflows:

1. **Retrieval (lightweight, GPU required but relatively cheap)**  
   Query a prebuilt LoRA metrics database using natural language and retrieve the most relevant LoRAs.

2. **Indexing (heavy, GPU-intensive)**  
   Download a new LoRA (e.g. from CivitAI), generate images, compute CLIP-based metrics, and upsert the result into a local database.

The project is designed as:
- a clean Python library (`pip install carlos`)
- reproducible via **conda**
- GPU-first (CUDA handled outside pip)
- safe for public use (no research artifacts exposed)

---

## Requirements & Assumptions

- **Python**: 3.9.x  
- **GPU**: NVIDIA GPU required
- **CUDA**: Managed via conda or PyTorch wheels
- **OS**: Linux recommended
- **Storage**: Parquet-backed database

> ⚠️ CPU-only execution is not supported.

---

## Installation

### Create Conda Environment

```bash
conda create -n carlos python=3.9.16 -y
conda activate carlos
```

### Install PyTorch with CUDA

```bash
python -m pip install --extra-index-url https://download.pytorch.org/whl/cu126 -r requirements-cu126.lock.txt
```

Verify:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

### Install CARLoS

```bash
pip install carlos
```

---

## Public API

Most users only need:

```python
import carlos
```

Main entry points:
- `carlos.copy_bundled_database`
- `carlos.load_database`
- `carlos.retrieve`
- `carlos.index_lora`

---

## Retrieval Example

```python
from pathlib import Path
import carlos

out_dir = Path("/path/to/output")
out_dir.mkdir(parents=True, exist_ok=True)

db_parquet = out_dir / "metrics_database.local.parquet"
carlos.copy_bundled_database(db_parquet, overwrite=False)
db = carlos.load_database(db_parquet)

queries = [
    "snowfall, cold winter scene, visible breath",
    "oil painting style",
    "pixel art style",
]

for q in queries:
    results = carlos.retrieve(db, q, top_k=10)
    print(f"\nQuery: {q}")
    for r in results:
        print(f"[{r.rank}] id={r.lora_id} score={r.score:.4f}")
```

---

## Indexing Example (GPU-Heavy)

```python
from pathlib import Path
import carlos

model_id = "2300298"
version_id = "2588340"

out_dir = Path("/path/to/output")
out_dir.mkdir(parents=True, exist_ok=True)

db_parquet = out_dir / "metrics_database.local.parquet"
carlos.copy_bundled_database(db_parquet, overwrite=False)
db = carlos.load_database(db_parquet)

result = carlos.index_lora(
    db,
    lora_source="civitai",
    model_id=model_id,
    version_id=version_id,
    overwrite=False,
    working_directory=out_dir / "work",
)

db.save_parquet(db_parquet)

print("Indexed:", result.row["version_id"])
print("Strength:", result.vector.strength)
print("Consistency:", result.vector.consistency)
```

---

## CivitAI Access (Optional)

```bash
export CIVITAI_API_KEY=your_key_here
```

---

## Development Philosophy

- `src/` layout
- `pyproject.toml`
- minimal public API
- no generated artifacts committed
- GPU runtime handled externally

---

## License

MIT License.
