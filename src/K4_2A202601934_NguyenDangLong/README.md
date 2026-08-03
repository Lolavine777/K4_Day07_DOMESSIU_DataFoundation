# Nguyen Dang Long - Reusable Deliverable

This package provides the personal ASOS product retrieval implementation for the lab.

## Components

- `HeadingRecursiveChunker` preserves Markdown heading hierarchy and recursively splits long sections.
- `LocalEmbedder` defaults to the multilingual `BAAI/bge-m3` model.
- `EmbeddingStore` indexes and searches document chunks.
- `KnowledgeBaseAgent` combines retrieval with an injected generative LLM function.
- `benchmark_results.json` records the 5-query benchmark evidence.

## Reuse

```python
from src.K4_2A202601934_NguyenDangLong import (
    Document,
    EmbeddingStore,
    HeadingRecursiveChunker,
    LocalEmbedder,
)
```

Run the benchmark from the repository root:

```bash
LAB_SOLUTION_PACKAGE=src.K4_2A202601934_NguyenDangLong \
EMBEDDING_PROVIDER=local \
LOCAL_EMBEDDING_MODEL=BAAI/bge-m3 \
.venv/bin/python benchmark/run_benchmark.py \
  --data-dir data/k4_asos_products \
  --chunker heading --chunk-size 400 --top-k 3 --markdown
```

The recorded BGE-M3 result is 10/10 for retrieval across the five golden queries.

The result file does not claim generative-answer verification until LLM responses are checked against the gold answers.
