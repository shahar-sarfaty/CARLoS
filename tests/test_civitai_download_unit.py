import json
import os
from types import SimpleNamespace

import pytest


class _FakeResponse:
    def __init__(self, payload_bytes: bytes, status_code: int = 200):
        self._payload = payload_bytes
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=1024 * 1024):
        # yield in chunks
        data = self._payload
        for i in range(0, len(data), max(1, chunk_size)):
            yield data[i : i + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_download_lora_writes_files_and_parses_json(monkeypatch, tmp_path):
    # index.py imports heavy deps (diffusers/torch/transformers). If your env doesn’t have them,
    # this test should be skipped rather than fail.
    pytest.importorskip("requests")
    try:
        import carlos.index as idx
    except Exception as e:  # pragma: no cover
        pytest.skip(f"carlos.index import failed in this environment: {e}")

    download_dir = tmp_path / "dl"
    model_id = 111
    version_id = 222

    version_meta = {"id": version_id, "name": "v"}
    model_meta = {"id": model_id, "name": "m"}

    # Route based on URL content
    def fake_get(url, stream=True, timeout=60):
        if f"/v1/model-versions/{version_id}" in url:
            return _FakeResponse(json.dumps(version_meta).encode("utf-8"))
        if f"/v1/models/{model_id}" in url:
            return _FakeResponse(json.dumps(model_meta).encode("utf-8"))
        if f"/download/models/{version_id}" in url and "format=SafeTensor" in url:
            return _FakeResponse(b"NOT_EMPTY_SAFETENSORS_BYTES")
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(idx.requests, "get", fake_get)

    safetensors_path, got_version_meta, got_model_meta = idx._download_lora(
        model_id=model_id,
        version_id=version_id,
        download_directory=str(download_dir),
        debug=True,
        civitai_key_str=None,
    )

    assert os.path.exists(safetensors_path)
    assert os.path.getsize(safetensors_path) > 0
    assert got_version_meta["id"] == version_id
    assert got_model_meta["id"] == model_id

    # Ensure the JSON files were written
    assert (download_dir / f"{version_id}.json").exists()
    assert (download_dir / f"{model_id}.json").exists()