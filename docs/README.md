# Documentation

Use this page to find the right level of detail.

## Start here

- [Design](design.md) explains the operation and target model, DOM identities, freshness checks, waits, and runtime limits.
- [Configuration and development](development.md) covers local setup, browser checks, recordings, and the Moli compatibility probe.
- [Performance](performance.md) records the current measurements, methods, and limits.
- [Internal production](internal-production.md) describes the fail-closed worker and its deployment controls.

## Architecture reference

- [Codebase graph](codebase-graph.md) explains modules, entry points, call paths, and deployment relationships.
- [Generated source inventory](codegraph/inventory.md) lists indexed files, imports, and definitions.
- [Generated call relationships](codegraph/calls.md) records static call and construction edges.
- [Graph verification](codegraph/verification.md) lists the commands used to refresh the graph.

Generated graph edges are navigation aids. They do not prove runtime behavior. Use source code and behavior checks for operational decisions.

## Recorded evidence

- [Prepared-step performance](performance-prepared.md) preserves results from the earlier prepared-step prototype.
- `measurement.json`, `flights-measurement.json`, `full-speed-measurement.json`, and related files contain raw measurement records.
- `demo.mp4`, `demo.gif`, and the PNG images show recorded runs.

Historical hashes, model identifiers, and commit-pinned links remain unchanged. They identify the code and providers used for those runs.

## Project records

The repository also keeps plans, release gates, and review snapshots. These files describe the revision or decision that produced them. They are not a substitute for the current README, design guide, tests, or source code.
