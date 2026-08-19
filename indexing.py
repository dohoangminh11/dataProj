from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR = Path("data")
EMBEDDINGS_PATH = DATA_DIR / "player_embeddings.npy"
PLAYER_IDS_PATH = DATA_DIR / "player_ids.npy"
METADATA_PATH = DATA_DIR / "player_embedding_metadata.json"


def _document_hash(text: str, model_name: str) -> str:
    """Identify the exact text/model combination used for an embedding."""
    content = f"{model_name}\0{text}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _load_existing_index(
    model_name: str,
) -> tuple[dict[int, np.ndarray], dict[int, str]]:
    paths = (EMBEDDINGS_PATH, PLAYER_IDS_PATH, METADATA_PATH)
    if not all(path.exists() for path in paths):
        return {}, {}

    try:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        if metadata.get("model_name") != model_name:
            return {}, {}

        player_ids = np.load(PLAYER_IDS_PATH)
        embeddings = np.load(EMBEDDINGS_PATH)
        if len(player_ids) != len(embeddings):
            return {}, {}

        cached_embeddings = {
            int(player_id): embedding
            for player_id, embedding in zip(player_ids, embeddings)
        }
        cached_hashes = {
            int(player_id): document_hash
            for player_id, document_hash
            in metadata["document_hashes"].items()
        }
        return cached_embeddings, cached_hashes
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return {}, {}


def build_or_update_index(
    documents: Mapping[int, str],
    model_name: str = MODEL_NAME,
    batch_size: int = 64,
) -> tuple[np.ndarray, np.ndarray]:
    """Embed only new or changed documents and persist the complete index."""
    if not documents:
        raise ValueError("At least one player document is required.")

    cached_embeddings, cached_hashes = _load_existing_index(model_name)
    current_hashes = {
        int(player_id): _document_hash(text, model_name)
        for player_id, text in documents.items()
    }
    changed_ids = [
        int(player_id)
        for player_id in sorted(documents)
        if cached_hashes.get(int(player_id)) != current_hashes[int(player_id)]
        or int(player_id) not in cached_embeddings
    ]

    if changed_ids:
        model = SentenceTransformer(model_name)
        new_embeddings = model.encode(
            [documents[player_id] for player_id in changed_ids],
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        cached_embeddings.update(
            zip(changed_ids, np.asarray(new_embeddings, dtype=np.float32))
        )

    ordered_ids = np.asarray(sorted(documents), dtype=np.int64)
    ordered_embeddings = np.stack(
        [cached_embeddings[int(player_id)] for player_id in ordered_ids]
    ).astype(np.float32)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.save(PLAYER_IDS_PATH, ordered_ids)
    np.save(EMBEDDINGS_PATH, ordered_embeddings)
    METADATA_PATH.write_text(
        json.dumps(
            {
                "model_name": model_name,
                "normalized": True,
                "document_hashes": {
                    str(player_id): current_hashes[int(player_id)]
                    for player_id in ordered_ids
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Indexed {len(ordered_ids)} players: "
        f"embedded {len(changed_ids)}, reused {len(ordered_ids) - len(changed_ids)}."
    )
    return ordered_ids, ordered_embeddings


def load_index() -> tuple[np.ndarray, np.ndarray]:
    """Load the persisted player IDs and embedding matrix."""
    if not PLAYER_IDS_PATH.exists() or not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError("No embedding index exists. Build it first.")
    return np.load(PLAYER_IDS_PATH), np.load(EMBEDDINGS_PATH)


def semantic_search(
    query: str,
    top_k: int = 5,
    model_name: str = MODEL_NAME,
) -> list[tuple[int, float]]:
    """Return player IDs with the highest cosine similarity to a query."""
    player_ids, embeddings = load_index()
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    model = SentenceTransformer(model_name)
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    scores = embeddings @ query_embedding
    best_indices = np.argsort(scores)[::-1][:top_k]
    return [
        (int(player_ids[index]), float(scores[index]))
        for index in best_indices
    ]
