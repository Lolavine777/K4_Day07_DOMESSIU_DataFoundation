# Nguyễn Đăng Long - 2A202601934

This directory is the complete reusable personal deliverable for Lab 7.

It contains the core chunking, embedding, vector store, agent implementation, the heading-aware personal strategy, reproducible experiments, benchmark evidence, and the personal report.

## Reproduce

```bash
LAB_SOLUTION_PACKAGE=src.K4_2A202601934_NguyenDangLong .venv/bin/python -m pytest tests -q
.venv/bin/python -m src.K4_2A202601934_NguyenDangLong.similarity_experiment
LAB_SOLUTION_PACKAGE=src.K4_2A202601934_NguyenDangLong EMBEDDING_PROVIDER=bgem3 \
  .venv/bin/python benchmark/run_benchmark.py --data-dir data/k4_asos_products \
  --chunker heading --chunk-size 400 --top-k 3 --markdown
```

The generative agent benchmark reads the existing OpenAI-compatible settings from `ui/.env` without committing credentials.

```bash
.venv/bin/python -m src.K4_2A202601934_NguyenDangLong.agent_benchmark
```

## Evidence

- `similarity_results.json` records five BGE-M3 cosine-similarity experiments.
- `benchmark_results.json` records 5/5 top-1 retrieval results.
- `agent_benchmark_results.json` records five generated answers and their human verification against the shared gold answers.
- `REPORT_CANHAN.md` maps the evidence to the 60-point personal rubric.
