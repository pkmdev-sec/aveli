# Gates: deployment and operations

Scope: Reproducible build, CI, container deployment, monitoring/runbook documentation, and explicit non-code release gates.

- [ ] G1: CI runs offline tests, real isolated-browser checks, JavaScript validation, and package build.
  EVIDENCE: `.github/workflows/ci.yml` contains SHA-pinned offline, browser, and container jobs. Local equivalents pass; hosted execution awaits a push.

- [ ] G2: Container deployment runs as non-root, uses one job per process, pins dependencies, and includes a health/smoke check.
  CHECK: python scripts/check_deployment.py
  EXPECT: DEPLOYMENT_CHECK_PASS
  EVIDENCE: Static deployment check and local health preflight pass. A local image build could not start because the Docker daemon is not running; hosted container CI remains required.

- [x] G3: Operations documentation defines metrics, redaction, kill switch, rollback, ownership, incident handling, and release thresholds.
  EVIDENCE: `docs/internal-production.md` documents each required operating control and the 500-run/99% release gate.
