"""Run the five golden queries through Long's retriever and a generative LLM."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from benchmark.queries import BENCHMARK
from benchmark.run_benchmark import base_doc_of, build_store

from . import BGEM3Embedder, HeadingChunker
from . import __name__ as PACKAGE_NAME
import importlib


def run() -> list[dict]:
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / "ui" / ".env", override=False)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OPENAI_BASE_URL"])
    model = os.environ["OPENAI_MODEL"]
    package = importlib.import_module(PACKAGE_NAME)
    store, _ = build_store(package, str(root / "data" / "k4_asos_products"), HeadingChunker(400), BGEM3Embedder())
    rows = []
    for item in BENCHMARK:
        if item.get("metadata_filter"):
            candidates = store.search_with_filter(item["query"], top_k=20, metadata_filter=item["metadata_filter"])
        else:
            candidates = store.search(item["query"], top_k=20)
        unique_results = []
        seen_docs = set()
        for result in candidates:
            doc_id = base_doc_of(result)
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                unique_results.append(result)
            if len(unique_results) == 3:
                break
        top_docs = [base_doc_of(result) for result in unique_results]
        expected = set(item["expected_doc_ids"])
        outcome = "TOP-1" if top_docs and top_docs[0] in expected else "TOP-3" if any(doc in expected for doc in top_docs) else "MISS"
        context = "\n\n".join(
            f"Source: {doc_id}\n{(root / 'data' / 'k4_asos_products' / f'{doc_id}.md').read_text(encoding='utf-8')}"
            for doc_id in top_docs
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Answer only from the supplied product context. Be concise and include every detail requested."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {item['query']}"},
            ],
        )
        rows.append({
            "query_id": item["id"],
            "query": item["query"],
            "gold_answer": item["gold_answer"],
            "top_docs": top_docs,
            "retrieval_outcome": outcome,
            "agent_answer": response.choices[0].message.content.strip(),
            "human_verified": False,
        })
    return rows


if __name__ == "__main__":
    output = Path(__file__).with_name("agent_benchmark_results.json")
    payload = {"embedding_model": "BAAI/bge-m3", "results": run()}
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output)
