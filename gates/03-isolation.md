# Gates: isolated one-job worker

Scope: Each production job owns an ephemeral Chrome profile and dedicated Browser Harness daemon, with cleanup and concurrency separation.

- [x] G1: Isolation unit tests prove unique profile/runtime directories, explicit CDP pinning, and cleanup on success and failure.
  CHECK: uv run pytest -q tests/test_isolation.py tests/test_worker.py
  EXPECT: /[1-9][0-9]* passed/
  EVIDENCE: Isolation/worker tests passed; worker passes exact hosts to the CONNECT proxy and uses unique profile/runtime paths.

- [x] G2: A real isolated Chrome runs all local freshness/execution checks without model calls.
  CHECK: uv run python scripts/run_isolated_checks.py
  EXPECT: /PASS: [1-9][0-9]* browser guard checks/
  EVIDENCE: Real Google Chrome 153.0.8010.48 completed `PASS: 22 browser guard checks; no model calls`.

- [x] G3: The worker emits a machine-readable typed result and redacted JSONL audit trail for a policy-denied offline job.
  CHECK: uv run python scripts/smoke_worker.py
  EXPECT: WORKER_SMOKE_PASS
  EVIDENCE: `scripts/smoke_worker.py` emitted `policy_denied`, made zero mutations, redacted audit data, and printed `WORKER_SMOKE_PASS`.

- [x] G4: Real Chrome cannot bypass the browser host allowlist through its implicit loopback exception.
  CHECK: uv run python scripts/check_network_isolation.py
  EXPECT: LOOPBACK_BLOCK_PASS
  EVIDENCE: Google Chrome 153.0.8010.48 made zero requests to a live loopback probe; the proxy audited the denial.
