# Internal production hardening plan

## Target

A one-job-per-process internal worker for named, low-risk workflows. Every job runs in an ephemeral Chrome profile, applies deterministic host/action policy before execution, and reports success only after an independent verifier passes.

## Caller contract

```python
spec = JobSpec.from_dict(payload)  # validates the external request once
settings = ProductionSettings.from_env(os.environ)  # requires pinned models and provider-data approval
with IsolatedChrome(spec.job_id, chrome_config, allowed_hosts=spec.allowed_hosts):
    result = ProductionRunner(
        settings, audit_sink=audit_sink, approval_provider=approval_provider
    ).run(spec)
```

The deployment entry point reads one JSON `JobSpec` from stdin, launches an isolated Chrome and Browser Harness daemon, runs the job, emits one JSON `JobResult`, then destroys the browser profile and exits.

## Module map

- `config.py`: validated provider/runtime settings from environment.
- `job.py`: immutable job, action-policy, verification, and result types.
- `runner.py`: production use-case orchestration around the existing `Agent`.
- `isolation.py`: ephemeral Chrome process/profile and dedicated Browser Harness runtime.
- `network.py`: fail-closed HTTPS CONNECT allowlist for browser network requests.
- `worker.py`: one-job CLI boundary.
- `audit.py`: redacted JSONL operational events.
- Existing `agent.py` remains the small decision loop; it gains only proposal/budget lifecycle seams needed by the runner.
- Existing `browser.py` retains DOM execution and receives proven race/cleanup/screenshot/select fixes.

## Phases

1. Define and test typed config, policy, verification, result, and runner contracts.
2. Fix known browser correctness/lifecycle defects with regressions.
3. Add ephemeral Chrome/daemon isolation and a one-job worker.
4. Add real-browser CI, deployment artifacts, audit/operations documentation, and release gates.
5. Run offline, isolated-browser, packaging, security, and diff verification.

## Non-code release gates

- Security approves provider data handling and retention.
- Workflow owners supply representative task corpora and deterministic verifiers.
- A pilot records at least 500 representative runs with >=99% verified success, zero policy escapes, and zero duplicate mutations.
- Financial, destructive, messaging, and account-changing operations retain human approval.

## Status log

- 2026-09-18: plan created from the verified repository evaluation; implementation authorized.
- 2026-09-18: contracts, policy, verification, browser fixes, isolation, network boundary, worker, tests, CI, deployment files, and runbook implemented.
- 2026-09-18: 86 offline tests and 22 real-Chrome checks plus the real loopback-block probe passed; package, lint, OSV, secret, worker-smoke, and deployment-static checks passed.
- 2026-09-18: independent final safety review found eight issues; all five high and three medium findings were fixed with regressions.
- 2026-09-18: production release remains blocked on hosted container CI, provider/security approval, a named workflow configuration, and soak evidence.
