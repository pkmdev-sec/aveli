# Analysis verification

Commands run against the current working tree:

- `codegraph --version`: 1.5.0.
- `codegraph init <temporary-source-copy>`: 42 files, 657 nodes, 1,483 edges.
- `uv run python docs/codegraph/export_graph.py <temporary-source-copy>`: all source-hash, edge-endpoint, and Python-declaration checks passed.
- Full prepare → fresh CodeGraph index → export: reproduced source hashes, graph counts, and Python imports.
- Deliberately changed temporary source: exporter rejected stale index before creating output.
- Repeated export from the same index: byte-identical graph.json, inventory.md, calls.md, and imports.mmd.
- `uv run pytest`: 91 passed in 2.87 seconds.
- `uv run ruff check .`: passed.
- `node --check aveli/static/app.js`: passed.
- `node --check aveli/snapshot.js`: passed.
- `uv build`: source distribution and wheel built.
- Report artifact links: all local targets exist.
- Source hashes in the refreshed graph match the temporary source snapshot; `uv lock` records the renamed `aveli` distribution.
- Repository .codegraph directory: not created. Indexing only occurred in temporary source copies.

No paid API calls, live examples, real-browser checks, Docker builds, or deployment validation were run.
