# Aveli codebase review and development adoption guide

## Review contract

This review covers the current working tree on `internal-production-hardening`, not only commit `452c1ad`. It covers the browser-agent loop, inspector, production worker, policy, isolation, audit, tests, scripts, deployment files, and operator documentation.

The review answers four questions:

1. What does the framework do?
2. Which design choices are strong?
3. What can fail or block production use?
4. How should a development team use it?

Media files and generated graph data were inventoried but not treated as application logic. I did not call paid model APIs, run hosted CI, build the Docker image, or produce the required production soak evidence.

For the exhaustive file and call inventory, see [the codebase graph](codebase-graph.md).

## Verdict

Aveli is a constrained browser agent, not a general browser-automation platform. Its useful idea is the boundary between model choice and code execution. The model chooses from controls that the browser has already observed. Code owns node identity, freshness checks, input, budgets, policy, audit, and final verification.

That shape is a good fit for adaptive acceptance tests and exploratory browser checks on development or staging systems. It is not a replacement for deterministic unit, API, component, or selector-based browser tests. It is also not ready for unattended consequential work on production systems.

The production shell is thoughtful and fail-closed in several important places. It still depends on external data approval, workflow-specific policy, hosted container evidence, and soak results. Two code boundaries also need tightening before the worker receives access to private networks or consequential controls.

## System model

```text
Natural-language goal
        |
        v
Browser snapshot: visible text + indexed, compatible controls
        |
        v
One TypeSafe request: operation + speculative target heads
        |
        +--> TYPE_TEXT only: small text model returns {"text": "..."}
        |
        v
Policy and optional approval freeze the exact proposal
        |
        v
Freshness, identity, visibility, and occlusion checks
        |
        v
Browser input, execution history, and a new observation
        |
        v
DONE requests independent URL/title/text verification
```

There are two execution boundaries:

- `aveli` runs a loopback inspector around one shared `Agent`. It is a demo and debugging tool.
- `aveli-internal-worker` reads one JSON job, creates an isolated Chrome profile, runs one bounded job, writes redacted audit events, prints one result, and exits.

The main runtime path is:

`Agent` -> `model.choose` -> `Browser.act` -> `snapshot.js` -> next observation.

The production path adds:

`worker.execute` -> `IsolatedChrome` -> `ProductionRunner` -> `ActionPolicy` -> `Agent` -> `VerificationSpec`.

## What is well designed

### The model cannot invent an execution mechanism

`snapshot.js` assigns code-owned identities to observed DOM nodes. The model receives finite choices, not permission to emit selectors, coordinates, JavaScript, or shell commands. `model.validate_choice` also rejects malformed probability distributions and choices outside the offered set.

### One model round trip carries operation and target choices

`model.choose` asks for an operation and operation-specific target heads in one request. The executor validates and consumes only the target head for the selected operation. This removes a serial model call while keeping click, text, and select targets separate.

### Mutation handling is conservative

`Agent.command("act")` consumes a decision before text generation or browser input. `Browser.act` checks the observed page again. The executor resolves current geometry, rejects hidden, disabled, replaced, read-only, or covered controls, and does not retry a browser mutation. History is recorded before the next observation, so a navigation failure cannot erase evidence that input occurred.

### Production concerns are outside the core loop

The production additions do not bury policy and deployment logic in `Agent`. Immutable job types, action policy, audit, process isolation, network controls, and verification live in separate modules. Lazy imports preserve the required order: isolation starts before Browser Harness loads.

### The verification and test posture is stronger than the demo framing suggests

A model `DONE` answer is not success. The runner applies configured URL, title, required-text, and forbidden-text checks. The repository also has focused offline tests, a real-Chrome guard suite, a network-denial probe, deployment checks, secret scanning, and an OSV lockfile scan.

### The codebase remains small

The primary runtime has 14 Python or standalone JavaScript files, plus inspector HTML and CSS assets. It has eight test modules and 13 operational or evidence scripts. The existing graph found no Python import cycles. The tracked-source diagnostic found 1.53% duplicate-line coverage. That duplication result excludes the untracked production modules, so it is supporting evidence, not a whole-tree quality claim.

## Review findings

### F1. High: action policy classifies browser mechanics, not business effects

**Evidence.** `snapshot.js:63-67` marks only native anchors, download anchors, and native submit controls with special effects. `job.py:251-269` classifies every other click as `interact`. `ActionPolicy` then allows, denies, or requests approval for that class.

**Impact.** A JavaScript button labelled "Delete", "Send", or "Approve" is only `interact`. A button can also submit a form or navigate without being a native submit control or anchor. Post-action host checks and the CONNECT proxy can limit destinations, but they cannot undo an allowed same-host side effect.

**Decision.** Do not allow broad `interact` on consequential production pages. For a named workflow, add a code-owned semantic action adapter or an explicit control allowlist. Bind policy to stable application metadata, such as test IDs and declared effects. Keep unknown controls denied.

### F2. High: provider data approval is global, not bound to a workflow

**Evidence.** `model.py:105-145` sends the goal, URL, title, visible text, element labels, current values, and recent generated text to TypeSafe. `model.py:152-198` sends a similar context to the text provider. `config.py:49-73` requires one `AVELI_EXTERNAL_DATA_APPROVED=true` flag, but the setting does not name approved hosts, workflows, fields, or provider endpoints.

**Impact.** Once the process flag is enabled, code does not prove that a new job's domain or data class received the same approval. URLs can also contain tokens or private query data. Prompt instructions reduce accidental obedience to page text, but they do not create a data-loss boundary.

**Decision.** Put approved workflow ID, exact hosts, provider IDs, and allowed data classes in a signed or immutable deployment policy. Reject jobs that do not match it. Use synthetic accounts and non-secret data for development checks. Prefer a self-hosted text provider when page content cannot leave the network.

### F3. Medium: the browser proxy checks hostnames but not resolved addresses

**Evidence.** `network.py:23-35` accepts an exact allowed hostname and calls `socket.create_connection((host, 443))`. It does not reject private, loopback, link-local, multicast, or reserved resolved addresses.

**Impact.** A permitted DNS name can resolve to a private address. The proxy therefore does not provide a complete private-network boundary by itself. The runbook correctly requires platform egress policy as a second boundary.

**Decision.** Resolve the hostname, reject disallowed address ranges, connect to an approved resolved address, and retain the hostname for TLS. Keep container or cluster egress policy as the authoritative second control. Add DNS-rebinding and private-address tests.

### F4. Medium: the exact-model contract is only partly enforced

**Evidence.** `config.py:21-25` rejects model names that end in `latest`. Any other mutable alias passes, although the error and runbook state that the model must be pinned to an exact version.

**Impact.** A provider can change behavior behind an accepted alias without a source or configuration change. That weakens reproducibility, approval evidence, and regression attribution.

**Decision.** Validate provider-specific immutable model or deployment IDs against an approved list. Record the returned provider model ID in audit and result metadata.

### F5. Medium: the central state machine is stringly typed and concentrated

**Evidence.** The structural diagnostic reports `Agent.command` at 111 source lines with AST complexity 29 and `browser_operation` at 81 source lines with complexity 17. The JavaScript `render` function is a 79-line heuristic hotspot. Page, action, decision, history, and result values cross JavaScript and Python as mutable dictionaries.

**Impact.** The current tests control this risk, but each new operation or browser feature must update several implicit schemas. Missed fields will appear at runtime. Extending the framework to frames, popups, file inputs, or keyboard actions will put more branches in the same functions.

**Decision.** Before adding operations, define typed `ObservedPage`, `ObservedAction`, `Decision`, and execution-result contracts. Split prediction, terminal transition, text preparation, mutation, and observation into named methods. Keep `Agent` as the orchestrator rather than adding layers around simple browser calls.

### F6. Medium: the release candidate exists only in the working tree

**Evidence.** The current branch points at the same commit as `main`, while the production modules, CI workflow, deployment files, gates, and many tests are modified or untracked. Gate R5 also states that hosted CI has not run and no image digest has been recorded.

**Impact.** Local passing checks do not publish the worker, enforce CI, or make the deployment reproducible for another checkout.

**Decision.** Review and commit the production change as a coherent patch. Run hosted CI, build the container, record its content digest, and keep the non-code release gates open until owners provide their evidence.

### F7. Low: the runbook overstates final observation freshness

**Evidence.** `agent.py:107-114` compares the live semantic marker with the stored page when the model chooses `DONE`. `runner.py:152-160` then verifies the stored page object. `docs/internal-production.md:11` says verification uses "a fresh observation."

**Impact.** The marker comparison is a useful freshness check, but it is not a new observation. The implementation and operating claim should say the same thing, especially when verification is a release boundary.

**Decision.** Either take a new observation after `DONE` and verify it, or state that the runner verifies a freshness-validated stored observation. Add a regression where the page changes between prediction and verification.

## Structural review

The module boundaries are mostly sound. `agent.py` owns use-case flow, `browser.py` owns CDP execution, `model.py` owns provider contracts, and `job.py` owns production domain rules. `runner.py` correctly acts as the production use-case orchestrator. `worker.py` and `isolation.py` keep process lifecycle outside domain logic.

The main coupling seam is the untyped action dictionary. These fields connect `snapshot.js`, `browser.py`, `model.py`, `agent.py`, `job.py`, `runner.py`, tests, and the inspector. That shared contract should become explicit before the operation set grows.

The second seam is process-global state. Browser Harness configuration, provider credentials, and active isolation use process environment or a module global. The one-job-per-process worker makes that acceptable. Do not turn `ProductionRunner` into a multi-tenant, threaded service without redesigning this ownership model.

## Best development uses

| Use case | Fit | Conditions |
|---|---|---|
| Adaptive smoke checks on preview or staging deployments | Strong | Synthetic data, exact HTTPS hosts, deterministic verifier, no consequential controls |
| Reproducing a reported UI journey | Strong | Capture goal, release digest, model IDs, final verifier result, and audit trail |
| Exploratory acceptance testing across changing layouts | Strong | Treat findings as evidence to inspect, not as deterministic pass/fail truth |
| Read-only checks in internal developer portals | Good | Restrict actions and hosts; approve provider data transfer |
| Form workflows with generated non-secret values | Conditional | Disposable environment, explicit submit policy, workflow-specific field rules |
| Pull-request blocking end-to-end test | Conditional | First prove low variance; keep deterministic tests as the main gate |
| Localhost development over HTTP | Weak in the production worker | `JobSpec` rejects loopback and HTTP; use a separate test-only isolation policy |
| Destructive production changes, payments, messages, or account changes | Poor | Mechanical action classes cannot authorize business effects safely |
| Canvas, closed shadow DOM, nested frames, uploads, popup-heavy or keyboard-heavy apps | Poor today | These controls are outside the current action and observation model |
| Unit, API, visual-diff, or accessibility conformance testing | Wrong tool | Use purpose-built deterministic tools |

## Recommended development workflow

Start with one narrow workflow: a read-only preview-deployment check.

Example goal:

> Open the release page for build `abc123`. Confirm that its status is `Ready` and that no failure banner is visible.

Example job shape:

```json
{
  "schema_version": 1,
  "job_id": "preview-abc123",
  "url": "https://preview.dev.example/releases/abc123",
  "goal": "Confirm build abc123 is Ready and no failure banner is visible.",
  "allowed_hosts": ["preview.dev.example"],
  "allowed_actions": ["navigate", "interact", "scroll", "wait"],
  "approval_required_actions": [],
  "verification": {
    "url_prefix": "https://preview.dev.example/releases/abc123",
    "title_contains": ["Release"],
    "required_text": ["abc123", "Ready"],
    "forbidden_text": ["Build failed", "Deployment failed"]
  },
  "timeout_seconds": 60,
  "max_actions": 12
}
```

Use this only on a read-only or disposable environment because `interact` is broad. If the page is already the target and needs no clicks, omit `interact`.

A practical delivery path is:

1. A preview-deployment event creates a versioned `JobSpec` from a reviewed workflow template.
2. A queue starts one worker container for that job.
3. The worker uses synthetic accounts and exact host policy.
4. A verifier checks visible state and, when possible, an authoritative application API.
5. The result and redacted audit events go to the build summary and metrics store.
6. The first phase is non-blocking shadow mode. Engineers inspect every failure class.
7. Promotion to a required check happens only after the team measures variance, cost, and false results on its own corpus.

Do not weaken production URL validation to make localhost work. Add a separate `LocalTestRunner` or explicit test-only `ChromeConfig` that permits loopback, starts a disposable profile, blocks external egress, and cannot be selected by the production entry point.

## Changes that unlock wider use

### Do first

1. Bind data approval and policy to a named workflow and provider set.
2. Close the hostname-to-private-address gap.
3. Add semantic control policy for any page with consequential actions.
4. Add a pluggable verifier that can query an API or database read model.
5. Commit the release candidate and run hosted container CI.

### Do when the first workflow proves value

1. Define typed cross-module action and page contracts.
2. Store a versioned corpus of goals, workflow policies, and verifier fixtures.
3. Record immutable model IDs, worker image digest, application revision, latency, action count, and token use.
4. Add failure taxonomy: unsupported control, policy denial, stale page, provider failure, verifier failure, and application defect.
5. Add DOM features only when corpus failures justify them. Frames and popups are likely before canvas or arbitrary keyboard widgets.

### Do not do

- Do not replace deterministic tests with agent runs.
- Do not share a production worker process across jobs.
- Do not give the model selectors, scripts, or unrestricted browser commands.
- Do not send credentials, source code, customer data, or signed URLs to external providers without explicit approval.
- Do not infer success from `DONE` or from a click receipt.

## Verification performed for this review

The following checks passed on the reviewed working tree:

- `uv run ruff check .`
- `uv run pytest -q`: 86 tests passed.
- JavaScript syntax checks for `static/app.js` and `snapshot.js`.
- `uv build`: wheel and source distribution built.
- `scripts/check_deployment.py`: `DEPLOYMENT_CHECK_PASS`.
- `scripts/smoke_worker.py`: policy denial occurred with zero mutations and a machine-readable result.
- `scripts/check_secrets.py`: no credential pattern found.
- `scripts/check_vulnerabilities.py`: no known OSV issue in 22 locked registry packages.
- `scripts/run_isolated_checks.py`: 22 real-Chrome guard checks passed without model calls.
- `scripts/check_network_isolation.py`: the loopback probe received no request.
- Structural diagnostic freshness check for `.agent-map/sloppiness.json` and `.agent-map/sloppiness.md`.

These checks do not prove live task reliability. I did not run paid TypeSafe or text-model calls, hosted CI, a Docker build, an allowed-host TLS tunnel test, or the 500-job soak gate.

## Final recommendation

Use Aveli as an adaptive browser-checking layer for development and staging. Keep the first workflows read-only, narrow, independently verified, and non-blocking. Preserve deterministic tests as the release foundation.

Do not market or deploy it as a general autonomous browser worker. The framework becomes credible for wider internal use after workflow-bound data policy, semantic action authorization, stronger network resolution checks, and authoritative verification are in place.
