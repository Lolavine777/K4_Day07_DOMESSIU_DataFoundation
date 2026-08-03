#!/usr/bin/env python3
"""Run the shared five-query benchmark across all five K4 strategies."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from benchmark.queries import BENCHMARK
from ingest import load_documents
from src.K4_2A202601934_NguyenDangLong import LocalEmbedder


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "k4_asos_products"
BGE_M3 = "BAAI/bge-m3"

TEAM_SPECS = [
    {"student_id": "2A202601078", "name": "Vũ Hữu An", "package": "src.K4_2A202601078_VuHuuAn", "strategy": "HeadingChunker", "factory": lambda p: p.HeadingChunker(max_chars=400)},
    {"student_id": "2A202601184", "name": "Đào Minh Chiến", "package": "src.K4_2A202601184_DaoMinhChien", "strategy": "RecursiveChunker-500", "factory": lambda p: p.RecursiveChunker(chunk_size=500)},
    {"student_id": "2A202601308", "name": "Lương Minh Quân", "package": "src.K4_2A202601308_LuongMinhQuan", "strategy": "FixedSize-500-overlap-50", "factory": lambda p: p.FixedSizeChunker(chunk_size=500, overlap=50)},
    {"student_id": "2A202601916", "name": "Lê Đăng Tấn", "package": "src.K4_2A202601916_LeDangTan", "strategy": "PolicySectionChunker", "factory": lambda p: p.PolicySectionChunker(chunk_size=500)},
    {"student_id": "2A202601934", "name": "Nguyễn Đăng Long", "package": "src.K4_2A202601934_NguyenDangLong", "strategy": "HeadingRecursiveChunker", "factory": lambda p: p.HeadingRecursiveChunker(chunk_size=400)},
]


def _build_store(package, chunker, embedder):
    store = package.EmbeddingStore(collection_name="team-benchmark", embedding_fn=embedder)
    documents = []
    for document in load_documents(DATA_DIR):
        for index, content in enumerate(chunker.chunk(document.content)):
            metadata = dict(document.metadata)
            metadata.update({"doc_id": document.id, "chunk_index": index})
            documents.append(package.Document(id=f"{document.id}::chunk_{index}", content=content, metadata=metadata))
    store.add_documents(documents)
    return store, len(documents)


def _base_doc(result: dict) -> str:
    return result.get("metadata", {}).get("doc_id") or result.get("doc_id", "")


def _unique_documents(results: list[dict], limit: int = 3) -> list[str]:
    output = []
    for result in results:
        doc_id = _base_doc(result)
        if doc_id and doc_id not in output:
            output.append(doc_id)
        if len(output) == limit:
            break
    return output


def _generate_answer(client: OpenAI | None, model: str, query: str, doc_ids: list[str]) -> str | None:
    if client is None:
        return None
    context = "\n\n".join(
        f"Source: {doc_id}\n{(DATA_DIR / f'{doc_id}.md').read_text(encoding='utf-8')}" for doc_id in doc_ids
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Answer only from the supplied product context. Be concise and include every detail requested."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return response.choices[0].message.content.strip()


def run() -> dict:
    load_dotenv(ROOT / "ui" / ".env", override=False)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()
    client = OpenAI(api_key=api_key, base_url=base_url) if api_key and base_url and model else None
    embedder = LocalEmbedder(BGE_M3)
    members = []
    for spec in TEAM_SPECS:
        package = importlib.import_module(spec["package"])
        chunker = spec["factory"](package)
        store, chunk_count = _build_store(package, chunker, embedder)
        query_results = []
        for item in BENCHMARK:
            if item.get("metadata_filter"):
                candidates = store.search_with_filter(item["query"], top_k=20, metadata_filter=item["metadata_filter"])
            else:
                candidates = store.search(item["query"], top_k=20)
            top_chunks = candidates[:3]
            top_docs = [_base_doc(result) for result in top_chunks]
            unique_docs = _unique_documents(candidates)
            expected = set(item["expected_doc_ids"])
            outcome = "TOP-1" if top_docs and top_docs[0] in expected else "TOP-3" if any(doc in expected for doc in top_docs) else "MISS"
            query_results.append({
                "query_id": item["id"],
                "outcome": outcome,
                "top_chunk_docs": top_docs,
                "top_unique_docs": unique_docs,
                "top_score": round(float(top_chunks[0]["score"]), 6) if top_chunks else None,
                "gold_answer": item["gold_answer"],
                "agent_answer": _generate_answer(client, model, item["query"], unique_docs),
                "answer_verified": False,
            })
        members.append({
            "student_id": spec["student_id"], "name": spec["name"], "package": spec["package"],
            "strategy": spec["strategy"], "embedding_model": BGE_M3, "chunk_count": chunk_count,
            "results": query_results,
        })
    return {"corpus": "data/k4_asos_products", "query_count": len(BENCHMARK), "members": members}


if __name__ == "__main__":
    output = ROOT / "benchmark" / "team_results.json"
    output.write_text(json.dumps(run(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(output)
