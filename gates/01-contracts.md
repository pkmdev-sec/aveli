# Gates: typed production contract

Scope: Validated job/config types, deterministic action policy, independent verification, typed results, and runner orchestration.

- [x] G1: External job and environment inputs are parsed into immutable validated types, rejecting unpinned models and missing provider-data approval.
  CHECK: uv run pytest -q tests/test_config.py tests/test_job.py
  EXPECT: /[1-9][0-9]* passed/
  EVIDENCE: `uv run pytest -q tests/test_config.py tests/test_job.py` passed (15 tests, 2026-09-18).

- [x] G2: Every proposed action is host/action-policy checked before execution and policy denial stops without browser mutation.
  CHECK: uv run pytest -q tests/test_runner.py -k policy
  EXPECT: /[1-9][0-9]* passed/
  EVIDENCE: Runner policy tests passed; denied actions made zero `act` calls (2026-09-18).

- [x] G3: A model DONE result becomes verified success only when the independent verifier passes.
  CHECK: uv run pytest -q tests/test_runner.py -k verif
  EXPECT: /[1-9][0-9]* passed/
  EVIDENCE: Verification tests passed; `DONE` with missing evidence returned `verification_failed` (2026-09-18).
