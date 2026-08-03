"""Reproduce Long's five BGE-M3 cosine-similarity predictions."""

import json
from pathlib import Path

from .chunking import compute_similarity
from .embeddings import LocalEmbedder


PAIRS = [
    ("This black cotton dress is available in several sizes.", "The black dress comes in multiple sizes.", "high"),
    ("The item is made from 100% cotton.", "The product uses a cotton main fabric.", "high"),
    ("This jacket is black.", "This jacket is bright red.", "low"),
    ("Dry clean only.", "Machine wash at 40 degrees.", "low"),
    ("The product is from adidas Originals.", "This item is made by Calvin Klein.", "low"),
]


def run() -> list[dict]:
    embedder = LocalEmbedder()
    results = []
    for index, (text_a, text_b, prediction) in enumerate(PAIRS, start=1):
        score = compute_similarity(embedder(text_a), embedder(text_b))
        results.append({"pair": index, "text_a": text_a, "text_b": text_b,
                        "prediction": prediction, "cosine_similarity": round(score, 6)})
    return results


if __name__ == "__main__":
    output = Path(__file__).with_name("similarity_results.json")
    output.write_text(json.dumps({"embedding_model": "BAAI/bge-m3", "results": run()}, indent=2), encoding="utf-8")
    print(output)
