# Gates: integrated release candidate

Scope: All existing behavior and new production boundaries pass together with a reviewable clean diff.

- [x] G1: Full offline quality suite passes.
  CHECK: uv run ruff check . && uv run pytest
  EXPECT: passed
  EVIDENCE: `uv run ruff check .` passed; `uv run pytest -q` passed 86 tests (2026-09-18).

- [x] G2: JavaScript and package artifacts validate.
  CHECK: node --check aveli/static/app.js && node --check aveli/snapshot.js && uv build
  EXPECT: Successfully built
  EVIDENCE: Both JavaScript checks passed; `uv build` produced wheel and sdist.

- [x] G3: Locked runtime dependencies have no known OSV vulnerabilities; dev-only findings are documented or fixed.
  CHECK: uv run python scripts/check_vulnerabilities.py
  EXPECT: NO_RUNTIME_VULNERABILITIES
  EVIDENCE: OSV batch scan returned `NO_RUNTIME_VULNERABILITIES` and `NO_LOCKED_VULNERABILITIES` for 22 packages.

- [x] G4: The implementation diff contains no credentials and unresolved release gates are explicit.
  CHECK: git diff --check && git grep -nE '(sk-[A-Za-z0-9_-]{20,}|TYPESAFE_API_KEY=.+)' -- ':!uv.lock' ':!.env.example' || true
  EXPECT: /^$/
  EVIDENCE: `git diff --check` and `scripts/check_secrets.py` passed with `NO_CREDENTIALS_FOUND`.
