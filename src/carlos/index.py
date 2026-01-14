# src/carlos/index.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile
import time
from typing import Optional, Any, Dict
import zipfile
import os
import requests
from tqdm import tqdm
import json
import random
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from PIL import Image
from diffusers import StableDiffusionXLPipeline
from transformers import CLIPProcessor, CLIPModel

from .generative_prompts import prompts_for_indexing, mini_set_of_prompts_for_quick_tests, micro_set_of_prompts_for_quick_tests
from .config import IndexingConfig, CIVITAI_API_KEY_ENV
from .database import * 
from .types import CarlosVector, IndexingResult


def _resolve_civitai_api_key(civit_key_str: Optional[str]) -> Optional[str]:
    # Precedence: explicit argument > environment > None
    if civit_key_str is not None and str(civit_key_str).strip() != "":
        return civit_key_str.strip()

    v = os.getenv(CIVITAI_API_KEY_ENV)
    if v is None or v.strip() == "":
        return None
    return v.strip()

def _unzip_and_extract(zip_path, target_suffix=".safetensors"):
    zip_dir = os.path.dirname(zip_path)       # Directory containing the zip file
    temp_dir = tempfile.mkdtemp()             # Temporary extraction directory

    # 1. Extract ZIP to temp directory
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_dir)

    # 2. Find the target file inside the extracted contents
    extracted_path = None
    for root, dirs, files in os.walk(temp_dir):
        for target_filename in files:
            if target_filename.endswith(target_suffix):
                extracted_path = os.path.join(root, target_filename)
                break

    if not extracted_path:
        shutil.rmtree(temp_dir)
        raise FileNotFoundError(f'"{target_filename}" not found in the ZIP.')

    # 3. Copy the file into the same directory as the ZIP
    copied_filename = os.path.basename(zip_path).replace(".zip", target_suffix)
    shutil.copy(extracted_path, os.path.join(zip_dir, copied_filename))

    # 4. Remove the ZIP file
    os.remove(zip_path)

    # 5. Clean temporary extraction directory
    shutil.rmtree(temp_dir)

    print(f"Extracted: {target_filename}")
    print(f"Copied to: {zip_dir}")
    print("ZIP deleted.")

def _download_lora(model_id, version_id, download_directory, debug=False, civitai_key_str=None):
    civitai_key_str = _resolve_civitai_api_key(civitai_key_str)

    os.makedirs(download_directory, exist_ok=True)

    def _build_url_and_target(id, file_type="safetensors"):
        if file_type == "safetensors":
            file_suffix = ".safetensors"
            url_suffix = "?type=Model&format=SafeTensor"
            api_directory = "download/models"
            token_suffix = ("&token=" + civitai_key_str) if civitai_key_str is not None else ""
        elif file_type == "archive":
            file_suffix = ".zip"
            url_suffix = "?type=Archive&format=Other"
            api_directory = "download/models"
            token_suffix = ("&token=" + civitai_key_str) if civitai_key_str is not None else ""
        elif file_type == "version_json":
            file_suffix = ".json"
            url_suffix = ""
            api_directory = "v1/model-versions"
            token_suffix = ("?token=" + civitai_key_str) if civitai_key_str is not None else ""
        elif file_type == "model_json":
            file_suffix = ".json"
            url_suffix = ""
            api_directory = "v1/models"
            token_suffix = ("?token=" + civitai_key_str) if civitai_key_str is not None else ""
        else:
            raise ValueError(
                f"\"{file_type}\" is an unsupported file type for download. "
                f"Try 'safetensors', 'archive', 'version_json', or 'model_json'."
            )

        target_saved_file_path = os.path.join(download_directory, f"{id}{file_suffix}")
        url = f"https://civitai.com/api/{api_directory}/{id}{url_suffix}{token_suffix}"
        return url, target_saved_file_path

    def _download_to_path(url: str, dst_path: str, *, timeout_s: int = 60):
        # Stream download to a temp file, then atomic replace.
        # This avoids leaving partial/corrupt files if interrupted.
        tmp_path = dst_path + ".part"

        if debug:
            # Avoid printing tokenized URL; give minimal info
            print(f"Downloading -> {dst_path}")

        try:
            with requests.get(url, stream=True, timeout=timeout_s) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            os.replace(tmp_path, dst_path)
        finally:
            # Clean up temp file if something went wrong
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    # 1) Download metadata JSONs (behavior preserved: saved as {id}.json)
    url, target_version_metadata_path = _build_url_and_target(version_id, "version_json")
    _download_to_path(url, target_version_metadata_path)

    url, target_model_metadata_path = _build_url_and_target(model_id, "model_json")
    _download_to_path(url, target_model_metadata_path)

    # 2) Download safetensors (behavior preserved: try safetensors first)
    url, target_saved_file_path = _build_url_and_target(version_id, "safetensors")
    _download_to_path(url, target_saved_file_path)

    # 3) Fallback: if safetensors is empty, try archive zip and extract .safetensors
    if os.path.getsize(target_saved_file_path) == 0:
        os.remove(target_saved_file_path)

        url, target_saved_zip_path = _build_url_and_target(version_id, "archive")
        _download_to_path(url, target_saved_zip_path)

        _unzip_and_extract(target_saved_zip_path, target_suffix=".safetensors")

        # After extraction, the .safetensors should exist at the original target path
        if os.path.getsize(target_saved_file_path) == 0:
            os.remove(target_saved_file_path)
            raise ValueError(
                f"\nDownloaded file size is 0 MB, deleted {target_saved_file_path}\n"
            )

    # 4) Load JSON and return (same as original)
    with open(target_version_metadata_path, "r") as f:
        version_metadata = json.load(f)
    with open(target_model_metadata_path, "r") as f:
        model_metadata = json.load(f)
    print(f"Downloaded LoRA version {version_id} for model {model_id} to {target_saved_file_path}")
    return target_saved_file_path, version_metadata, model_metadata

def _load_lora_weights_with_retries(pipe, lora_model_path, max_retries=5, wait_seconds=10):
    if lora_model_path is not None:
        for i in range(max_retries):
            try:
                pipe.load_lora_weights(lora_model_path, adapter_name=os.path.basename(lora_model_path).replace(".safetensors", ""))
                success = True
                break
            except:
                print("Retrying to load LoRA weights...")
                time.sleep(wait_seconds)
                success = False
        
        if not success:
            raise RuntimeError(f"Failed to load LoRA weights from {lora_model_path} after multiple attempts.")
    else:
        success = True
        print("No LoRA weights to load, proceeding without LoRA.")
    return pipe
    
def _get_SDXL_pipeline(models_cache_dir=None, device="cuda"):
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, cache_dir=models_cache_dir)
    pipe = pipe.to(device)
    pipe.safety_checker = None
    return pipe

def _load_clip_model(models_cache_dir=None, device="cuda", max_retries=5, wait_seconds=10):
    model_name = "openai/clip-vit-base-patch32"  # You can replace with another CLIP model
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

    return model, processor

def _is_single_prompt_dir_complete(prompt_dir, lora_name=None, number_of_images=16):
    contents = os.listdir(prompt_dir)
    subdirs = [d for d in contents if os.path.isdir(os.path.join(prompt_dir, d))]
    files = [f for f in contents if os.path.isfile(os.path.join(prompt_dir, f))]
    
    # Check if the directory contains exactly 3 subdirectories with the right names and no files
    if len(subdirs) != 2 or len(files) != 0:
        return False
    wanted_images_dir_name = "untriggered_images" if lora_name == "no_lora" or lora_name is None else "triggered_images"
    if set(subdirs) != set([wanted_images_dir_name, "clip_embeddings"]):
        return False

   # for every subdir, check if it contains 16 images or 16 embeddings 
    for subdir in subdirs:
        if len(os.listdir(os.path.join(prompt_dir, subdir))) < number_of_images:
            return False
    
    # If we got here, it means the prompt directory is complete
    return True

def _save_clip_embedding(model, processor, images_dir, device="cuda"):
    parent_dir = os.path.dirname(images_dir)
    clip_embedding_dir = os.path.join(parent_dir, f"clip_embeddings")
    if os.path.isdir(clip_embedding_dir) and len(os.listdir(clip_embedding_dir)) == len(os.listdir(images_dir)):
        return True
    
    os.makedirs(clip_embedding_dir, exist_ok=True)
    if len(os.listdir(clip_embedding_dir)) == len(os.listdir(images_dir)):
        print(f"Skipping {images_dir}. Already exists.")
        return True
  
    image_paths = [os.path.join(images_dir, image) for image in os.listdir(images_dir)]
    images = [Image.open(path) for path in image_paths]
    max_batch_size = 16

    for i in range(0, len(images), max_batch_size):
        inputs = processor(images=images[i:i + max_batch_size], return_tensors="pt", padding=True).to(device=device)
        with torch.no_grad():
            embeddings = model.get_image_features(**inputs)
        
        for j, embedding in enumerate(embeddings):
            output_path = os.path.join(clip_embedding_dir, f"image_{i + j}.pt")
            torch.save(embedding.cpu().numpy(), output_path)
    return True

def _free_text_to_filename(text, max_length=70):
    return text[:max_length].replace(" ", "_").replace(",", "_").replace(".", "_")

def _create_lora_name(version_metadata):
    model_file = None
    if version_metadata is None or "files" not in version_metadata.keys():
        raise ValueError("version_metadata is None or does not contain 'files' key.")
    
    for file in version_metadata["files"]:
        if file["type"].lower() == "model" and \
            "format" in file["metadata"].keys() and \
            file["metadata"]["format"].lower() == "safetensor" and \
                ((file["name"].split(".")[-1].lower() == "safetensors") or (file["name"].split(".")[1].lower() == "safetensors")):
            model_file = file
            break
    if model_file is None:
        raise ValueError("No model file found in the version_metadata files.")

    model_raw_name = model_file["name"]
    model_id = version_metadata["id"]

    lora_name = model_raw_name.split(".")[0] + "_" + str(model_id)
    return lora_name

def _get_triggers_from_metadata(version_metadata):
    if "trainedWords" in version_metadata.keys() and version_metadata["trainedWords"] is not None:
        triggers = version_metadata["trainedWords"]
    else:
        triggers = [""]
    return triggers

def get_seeds(num_seeds=16):
    return [str(s) for s in range(num_seeds)]

def save_dataframe_with_tensors(df, tensor_columns, file_path):
    for col in tensor_columns:
        df[col] = df[col].apply(lambda x: x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x)
    df.to_parquet(file_path, index=False)
    for col in tensor_columns:
        df[col] = df[col].apply(lambda x: torch.from_numpy(x) if isinstance(x, np.ndarray) else x)

def calculate_mean_pairwise_cosine_similarity(tensor_group):
    """Calculate pairwise cosine similarities for a tensor group."""
    # Convert tensors to NumPy array for efficient pairwise computation
    group_array = tensor_group.numpy()
    pairwise_sim = cosine_similarity(group_array)
    # Extract upper triangle (excluding diagonal) to avoid redundant comparisons
    upper_triangle_indices = np.triu_indices_from(pairwise_sim, k=1)
    pairwise_values = pairwise_sim[upper_triangle_indices]
    mean_pairwise = torch.tensor(np.mean(pairwise_values))
    return mean_pairwise

def calculate_mean_l2_norm(tensor_group):
    """Calculate mean L2 norm for a tensor group."""
    return torch.mean(torch.norm(tensor_group, dim=1))

def calculate_mean_vector(tensor_group):
    """Calculate mean vector for a tensor group."""
    return torch.mean(tensor_group, dim=0)

def delete_subdirectories(directory):
    """Delete all subdirectories in the given directory, but keep files."""
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"Deleted all subdirectories in {directory}, kept files intact.")
    except Exception as e:
        print(f"Warning: failed to cleanup generated dirs: {e}")
### pipeline ###

def _generate_images_for_one_prompt(pipe, with_lora, triggers: list[str], prompt: str, save_dir=None, cfg: IndexingConfig = IndexingConfig()):
    
    if with_lora:
        assert triggers is not None, "Triggers must be provided when using a LoRA."
        for trigger in triggers:
            prompt += f", {trigger}"
        lora_scale = cfg.lora_scale
    else:
        lora_scale = 0.0  # ensure no LoRA influence

    assert cfg.num_images_per_prompt % cfg.max_batch_size == 0 or cfg.num_images_per_prompt < cfg.max_batch_size, f"max_batch_size ({cfg.max_batch_size}) must be divisible by num_images_per_prompt ({cfg.num_images_per_prompt})"
    batch_size = cfg.max_batch_size if cfg.num_images_per_prompt >= cfg.max_batch_size else cfg.num_images_per_prompt
    all_images = []
    with torch.no_grad():
        for curr_seed in range(cfg.initial_seed, cfg.initial_seed+cfg.num_images_per_prompt, cfg.max_batch_size):
            if cfg.workload_type == "dry_run":
                images = [Image.new("RGB", (1024, 1024), color=tuple(random.randint(0, 255) for _ in range(3))) for _ in range(batch_size)]
            else:
                images = pipe(
                    prompt, 
                    num_inference_steps=cfg.num_inference_steps, 
                    cross_attention_kwargs={"scale": lora_scale},
                    generator=torch.manual_seed(curr_seed),
                    num_images_per_prompt=batch_size,
                ).images
            
            all_images.extend(images)
            torch.cuda.empty_cache()
    
    images_dir = os.path.join(save_dir, "triggered_images" if with_lora else "untriggered_images")
    os.makedirs(images_dir, exist_ok=True)
    for i, image in enumerate(all_images):
        image_save_path = os.path.join(images_dir, f"{i}.png")
        image.save(image_save_path)
    return all_images, images_dir

def _single_prompt_handling(pipe, with_lora, triggers, clip_model, clip_processor, prompt, save_dir, cfg: IndexingConfig = IndexingConfig()):

    _, images_dir = _generate_images_for_one_prompt(pipe, with_lora, triggers, prompt, save_dir=save_dir, cfg=cfg)
    
    _save_clip_embedding(clip_model, clip_processor, images_dir, device=cfg.device)
    
    if cfg.thumbnail_size is not None:
        for image_file in os.listdir(images_dir):
            image_path = os.path.join(images_dir, image_file)
            if image_file.endswith((".png", ".jpg", ".jpeg")) and os.path.isfile(image_path):
                with Image.open(image_path) as img:
                    img.thumbnail(cfg.thumbnail_size)
                    img.save(image_path, format="PNG")

def _single_lora_handling(downloaded_lora_path, lora_name, triggers, prompts, cfg: IndexingConfig = IndexingConfig()):
    pipe = _get_SDXL_pipeline(models_cache_dir=cfg.models_cache_dir, device=cfg.device)
    pipe = _load_lora_weights_with_retries(pipe, lora_model_path=downloaded_lora_path)
    clip_model, clip_processor = _load_clip_model(models_cache_dir=cfg.models_cache_dir, device=cfg.device)

    lora_dir = os.path.join(cfg.working_directory, lora_name if lora_name is not None else "no_lora")
    os.makedirs(lora_dir, exist_ok=True)

    with tqdm(total=sum(len(prompts[category][sub_category]) for category in prompts for sub_category in prompts[category]), desc="Processing", disable=False) as progress_bar:
        for category, sub_categories in prompts.items():
            category_dir = os.path.join(lora_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            for sub_category, prompts_list in sub_categories.items():
                sub_category_dir = os.path.join(category_dir, _free_text_to_filename(sub_category))
                os.makedirs(sub_category_dir, exist_ok=True)
                for prompt in prompts_list:
                    prompt_dir = os.path.join(sub_category_dir, _free_text_to_filename(prompt))
                    os.makedirs(prompt_dir, exist_ok=True)
                    if not _is_single_prompt_dir_complete(prompt_dir, lora_name=lora_name, number_of_images=cfg.num_images_per_prompt):
                        _single_prompt_handling(pipe, lora_name is not None, triggers, clip_model, clip_processor, prompt, save_dir=prompt_dir, cfg=cfg)
                    else:
                        print(f"Skipping prompt (already complete): {prompt}")
                    progress_bar.update(1)
    return lora_dir

def calculate_single_diff(generations_root_dir, lora_name, category, subcategory, prompt, seed):
    try:
        no_lora_vector = torch.load(os.path.join(generations_root_dir, "no_lora", category, _free_text_to_filename(subcategory), _free_text_to_filename(prompt), "clip_embeddings", f'image_{seed}.pt'), weights_only=False)
        lora_vector = torch.load(os.path.join(generations_root_dir, lora_name, category, _free_text_to_filename(subcategory), _free_text_to_filename(prompt), "clip_embeddings", f'image_{seed}.pt'), weights_only=False)
        diff = lora_vector - no_lora_vector
    except EOFError as e:
        print(f"EOFError encountered while loading embeddings for lora: {lora_name}, category: {category}, subcategory: {subcategory}, prompt: {prompt}, seed: {seed}.\n Error: {e}")
        return None
    except FileNotFoundError as e:
        print(f"FileNotFoundError encountered while loading embeddings for lora: {lora_name}, category: {category}, subcategory: {subcategory}, prompt: {prompt}, seed: {seed}.\n Error: {e}")
        return None
    return diff

def caclulate_clip_diffs_for_all_generations(lora_name, prompts, cfg: IndexingConfig = IndexingConfig()):
    rows = []
    for category in list(prompts.keys()):
        for subcategory in list(prompts[category].keys()):
            for prompt in prompts[category][subcategory]:
                for seed in get_seeds(num_seeds=cfg.num_images_per_prompt):
                    diff = calculate_single_diff(cfg.working_directory, lora_name, category, subcategory, prompt, seed)
                    row = {
                        "lora_name": lora_name,
                        "category": category,
                        "subcategory": subcategory,
                        "prompt": prompt,
                        "seed": seed,
                        "diff": diff 
                    }
                    rows.append(row)
    return pd.DataFrame(rows)

def calculate_metrics(df):
    stacked_diffs = torch.stack([torch.from_numpy(d) if isinstance(d, np.ndarray) else d for d in df["diff"].tolist() if d is not None and (isinstance(d, torch.Tensor) or isinstance(d, np.ndarray))])
    direction = calculate_mean_vector(stacked_diffs)
    strength = calculate_mean_l2_norm(stacked_diffs)
    consistency = calculate_mean_pairwise_cosine_similarity(stacked_diffs)
    return direction, strength, consistency

def build_metrics_row(
    version_metadata: Dict[str, Any],
    model_metadata: Dict[str, Any],
    lora_name: str,
    direction: np.ndarray,
    strength: float,
    consistency: float,
    ) -> Dict[str, Any]:
    """
    Canonical, stable row schema for both:
      - DB upsert (IndexingResult.row)
      - metrics.parquet / metrics.csv export

    Keep keys aligned with DEFAULT_REQUIRED_COLUMNS in database.py.
    """
    direction_np = np.asarray(direction, dtype=np.float32).reshape(-1)

    return {
        "version_id": int(version_metadata["id"]),
        "model_id": int(model_metadata.get("id") or 0) or None,  # allow None if missing
        "model_name": (model_metadata.get("name") or ""),
        "folder_name": lora_name,
        "model_description": (model_metadata.get("description") or ""),
        "model_download_count": int(((model_metadata.get("stats") or {}).get("downloadCount")) or 0),
        "model_nsfw_level": int(model_metadata.get("nsfwLevel") or 0) if model_metadata.get("nsfwLevel") is not None else None,
        "direction": direction_np,
        "strength": float(strength),
        "consistency": float(consistency),
    }


def metrics_dataframe_from_row(row: Dict[str, Any]) -> pd.DataFrame:
    """
    Single-row dataframe with columns in a stable order.
    """
    cols = list(DEFAULT_REQUIRED_COLUMNS)
    # Ensure all required columns exist (even if None)
    normalized = {c: row.get(c, None) for c in cols}
    return pd.DataFrame([normalized], columns=cols)

def local_test_indexing():
    version_id = "2093616"  # Example LoRA ID
    model_id = "1850005"  # Example LoRA ID
    cfg = IndexingConfig()
    cfg = cfg.with_overrides(num_images_per_prompt=1, workload_type="dry_run")
    os.makedirs(cfg.working_directory, exist_ok=True)
    prompts = micro_set_of_prompts_for_quick_tests()

    downloaded_lora_path, downloaded_version_metadata_path, downloaded_model_metadata_path = _download_lora(model_id=model_id, version_id=version_id, download_directory=cfg.working_directory, debug=False, civitai_key_str=cfg.civitai_key_str)
    with open(downloaded_version_metadata_path, 'r') as f:
        version_metadata = json.load(f)
    with open(downloaded_model_metadata_path, 'r') as f:
        model_metadata = json.load(f)

    triggers = _get_triggers_from_metadata(version_metadata)
    lora_name = _create_lora_name(version_metadata)
    _single_lora_handling(downloaded_lora_path=None, lora_name=None, triggers=[""], prompts=prompts, cfg=cfg)   # 1. Generate baseline without LoRA
    lora_dir = _single_lora_handling(downloaded_lora_path, lora_name, triggers, prompts, cfg=cfg)               # 2. Generate with LoRA
    clip_diff_df = caclulate_clip_diffs_for_all_generations(lora_name, prompts=prompts, cfg=cfg)                # 3. Calculate CLIP diffs
    direction, strength, consistency = calculate_metrics(clip_diff_df)                                          # 4. Calculate metrics
    
    if not cfg.save_generated_images_and_embeddings:
        delete_subdirectories(lora_dir)
    if not cfg.save_downloaded_model:
        os.remove(downloaded_lora_path)
    if cfg.save_raw_clip_diffs:
        save_dataframe_with_tensors(clip_diff_df, tensor_columns=["diff"], file_path=os.path.join(lora_dir, "clip_diffs.parquet"))
        metrics_df = create_metrics_dataframe(version_metadata, model_metadata, lora_name, direction, strength, consistency)
        save_dataframe_with_tensors(metrics_df, tensor_columns=["direction", "strength", "consistency"], file_path=os.path.join(lora_dir, "metrics.parquet"))
        metrics_df.to_csv(os.path.join(lora_dir, "metrics.csv"), index=False) # for easier viewing

    return direction, strength, consistency

def index_lora(
    db: CarlosDatabase,
    lora_source: str | Path,
    *,
    model_id: str | None = None,
    version_id: str | None = None,
    overwrite: bool = False,
    working_directory: Optional[Path] = None,
    civitai_key_str: Optional[str] = None,
    cfg: IndexingConfig = IndexingConfig(),
    ) -> IndexingResult:
 
    if version_id is None or model_id is None:
        raise ValueError("index_lora currently requires both model_id and version_id.")

    if "cuda" in cfg.device and not torch.cuda.is_available():
        print("Error: CUDA device specified but not available. CUDA is required for indexing.")
        raise RuntimeError("CUDA device specified but not available. CUDA is required for indexing.")

    # If already exists and not overwriting, return existing vector/row
    df = db.to_dataframe()
    if "version_id" in df.columns:
        hit = df[df["version_id"] == version_id]
        if not hit.empty and not overwrite:
            row = hit.iloc[0].to_dict()
            vec = db.get_vector(key="version_id", value=version_id)
            return IndexingResult(
                lora_id=str(version_id),
                vector=vec,
                row=row,
            )
    
    if working_directory is not None:
        cfg = cfg.with_overrides(working_directory=working_directory)
    if civitai_key_str is not None:
        cfg = cfg.with_overrides(civitai_key_str=civitai_key_str)

    if cfg.workload_type == "dry_run":
        cfg = cfg.with_overrides(num_images_per_prompt=1)
        prompts = mini_set_of_prompts_for_quick_tests()
    elif cfg.workload_type == "smoke_test":
        cfg = cfg.with_overrides(num_images_per_prompt=2)
        prompts = micro_set_of_prompts_for_quick_tests()
    elif cfg.workload_type == "mini_test":
        cfg = cfg.with_overrides(num_images_per_prompt=2)
        prompts = mini_set_of_prompts_for_quick_tests()
    elif cfg.workload_type == "full":
        cfg = cfg.with_overrides(num_images_per_prompt=16)
        prompts = prompts_for_indexing()
    os.makedirs(cfg.working_directory, exist_ok=True)

    # Get LoRA file path and metadata
    downloaded_lora_path, version_metadata, model_metadata = _download_lora(model_id=model_id, version_id=version_id, download_directory=cfg.working_directory, debug=False, civitai_key_str=cfg.civitai_key_str)
    triggers = _get_triggers_from_metadata(version_metadata)
    lora_name = _create_lora_name(version_metadata)

    _single_lora_handling(downloaded_lora_path=None, lora_name=None, triggers=[""], prompts=prompts, cfg=cfg)   # 1. Generate baseline without LoRA
    lora_dir = _single_lora_handling(downloaded_lora_path, lora_name, triggers, prompts, cfg=cfg)               # 2. Generate with LoRA
    clip_diff_df = caclulate_clip_diffs_for_all_generations(lora_name, prompts=prompts, cfg=cfg)                # 3. Calculate CLIP diffs
    direction, strength, consistency = calculate_metrics(clip_diff_df)                                          # 4. Calculate metrics

    row = build_metrics_row(
        version_metadata=version_metadata,
        model_metadata=model_metadata,
        lora_name=lora_name,
        direction=direction,
        strength=strength,
        consistency=consistency,
    )
    
    direction_np = np.asarray(row["direction"], dtype=np.float32).reshape(-1)

    result = IndexingResult(
        lora_id=str(version_id),
        vector=CarlosVector(direction=direction_np, strength=float(row["strength"]), consistency=float(row["consistency"])),
        row=row,
    )

    if cfg.workload_type == "full":
        db.upsert_indexing_result(result)

    # Save or clean up based on config
    if not cfg.save_generated_images_and_embeddings:
        delete_subdirectories(lora_dir)
    if not cfg.save_downloaded_model:
        try:
            os.remove(downloaded_lora_path)
        except Exception as e:
            print(f"Warning: failed to delete downloaded LoRA file: {e}")
    if cfg.save_raw_clip_diffs:
        save_dataframe_with_tensors(clip_diff_df, tensor_columns=["diff"], file_path=os.path.join(lora_dir, "clip_diffs.parquet"))
        metrics_df = metrics_dataframe_from_row(row)
        save_dataframe_with_tensors(metrics_df, tensor_columns=["direction", "strength", "consistency"], file_path=os.path.join(lora_dir, "metrics.parquet"))
        metrics_df.to_csv(os.path.join(lora_dir, "metrics.csv"), index=False) # for easier viewing

    return result