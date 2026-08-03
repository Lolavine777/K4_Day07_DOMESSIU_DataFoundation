"""Regression checks for the K4 policy corpus and its five shared queries."""

from __future__ import annotations

import csv
from pathlib import Path

from benchmark.queries import BENCHMARK
from ingest import load_documents


REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO_ROOT / "data" / "k4_ecommerce"
REQUIRED_METADATA = {
    "doc_id",
    "source_url",
    "retrieved_at",
    "document_version",
    "customer_role",
    "policy_area",
}


def test_k4_corpus_has_between_five_and_ten_policy_documents() -> None:
    documents = load_documents(CORPUS_DIR)
    assert 5 <= len(documents) <= 10
    assert all(document.metadata.get("policy_area") for document in documents)


def test_k4_documents_have_required_traceability_metadata() -> None:
    for document in load_documents(CORPUS_DIR):
        assert REQUIRED_METADATA.issubset(document.metadata)
        assert document.metadata["customer_role"] in {"buyer", "seller", "both"}


def test_sources_inventory_matches_the_policy_corpus() -> None:
    with (CORPUS_DIR / "sources.csv").open(encoding="utf-8", newline="") as source_file:
        source_rows = list(csv.DictReader(source_file))
    document_ids = {document.id for document in load_documents(CORPUS_DIR)}
    assert {row["doc_id"] for row in source_rows} == document_ids
    assert all(row["license_or_permission"] == "public-page" for row in source_rows)


def test_benchmark_has_exactly_five_grounded_queries_and_role_filter() -> None:
    document_ids = {document.id for document in load_documents(CORPUS_DIR)}
    assert len(BENCHMARK) == 5
    assert any(
        item["metadata_filter"] and item["metadata_filter"].get("customer_role") in {"buyer", "seller"}
        for item in BENCHMARK
    )
    for item in BENCHMARK:
        assert set(item["expected_doc_ids"]).issubset(document_ids)
