# Internal production worker

This mode runs one bounded browser job in one operating-system process and one ephemeral Chrome profile. It is for named internal domains and approved low-risk workflows. It is not a general browsing service.

## Safety boundary

The model can choose only an action that `snapshot.js` observed. It cannot supply CSS selectors, XPath, JavaScript, shell commands, or arbitrary browser operations. Code classifies the chosen action and checks the host, action class, approval, stale-page guard, deadline, and action budget before execution.

The worker records `action_executing` before a browser mutation. It never retries a mutation. It may predict again after a stale read-only observation. A `TYPE_TEXT` value is discarded after any stale context; the value is reusable only as part of the same immutable proposal and page fingerprint.

Model `DONE` means "request verification." It does not mean success. `ProductionRunner` checks the configured URL prefix and required or forbidden text against the latest observation returned by the agent. A result succeeds only when its status is `verified` and includes verification evidence.

## Data boundary and credentials

Both TypeSafe and the configured text-model provider receive page-derived data. TypeSafe receives visible page text, the indexed action space and labels, URL, title, goal, and recent actions including generated text. The text model receives the goal, visible page text and title, field metadata/current value, page fingerprint/URL, and recent generated text for `TYPE_TEXT`. Do not approve a domain until its data owner and security reviewer approve both transfers.

Set `AVELI_EXTERNAL_DATA_APPROVED=true` only in the deployment secret or configuration system after approval. The worker otherwise fails closed. Provider keys stay in environment-backed secrets and are never accepted in job JSON. `TYPESAFE_BASE_URL` and `TEXT_MODEL_BASE_URL` must use HTTPS. Model names that end in `latest` are rejected; use a versioned model name.

### Redaction

Audit output is JSONL in `AVELI_AUDIT_DIR`. Key, token, secret, password, authorization, cookie, and typed-value fields are redacted. Raw page text, screenshots, provider prompts, and credentials are not written. Treat labels and URLs as internal metadata because they can still contain sensitive content.

## Job contract

Use `deploy/job.example.json` as the schema example. `schema_version` must be `1`; incompatible future contracts will reject rather than guess. Important controls are:

- `allowed_hosts`: exact lower-case hosts. Subdomains are not implied.
- `allowed_actions`: automatic action classes. Use the smallest set.
- `approval_required_actions`: allowed only when a trusted callback approves the exact immutable proposal. The stock CLI has no callback, so it denies these actions. `type_text` cannot use this path because text is generated later; it must be denied or automatic only in a separately approved non-secret workflow.
- `verification`: independent URL/text assertions.
- `timeout_seconds` and `max_actions`: hard per-job budgets checked between provider/browser calls.

Unknown keys and invalid combinations are rejected. Redirects to an undeclared host fail the job before another action. Links whose observed `href` leaves the allowlist are denied before click. Chrome also uses a local CONNECT proxy that permits only declared hosts on HTTPS port 443; undeclared requests are blocked before connection and audited. Platform egress policy remains a required second boundary.

## Run one job

Build a versioned image. The Dockerfile pins the Python base image by digest, verifies the uv wheel checksum, and pins the Chrome package version. Record the resulting image digest in the deployment manifest; deploy by digest, not by a mutable tag.

```sh
docker build -f deploy/Dockerfile -t registry.internal/aveli-worker:$GIT_SHA .
docker run --rm -i   --env-file /run/secrets/aveli.env   --read-only   --tmpfs /tmp/aveli:rw,noexec,nosuid,size=512m   --mount type=volume,src=aveli-audit,dst=/var/log/aveli   --shm-size=1g   registry.internal/aveli-worker:$GIT_SHA < deploy/job.example.json
```

Run as the image's non-root user. Keep the Chrome sandbox enabled. Do not add `--no-sandbox`. Apply the platform's default seccomp profile, a read-only root filesystem, no inbound network ports, and egress rules limited to approved site and provider endpoints. Run exactly one job per container. Container teardown is the final cleanup boundary if the worker is killed.

Expected output is one JSON object. Its final URL is reduced to origin plus `/<redacted>`; verification results contain stable check IDs rather than configured secret text. Exit code 0 requires `status: verified`; policy denial, failed verification, timeout, or execution failure is nonzero. Persist the matching audit JSONL before deleting the container.

## Approval integration

The CLI deliberately has no interactive approval channel. A workflow that needs a consequential action must enter `IsolatedChrome` with exactly the job's hosts, then run `ProductionRunner` in that isolated job process and inject an `approval_provider(job, proposal)` callback connected to the internal approval service. Bind the approval to `job_id`, page fingerprint, observed node identity, action class, and proposal content. Reject expired or changed proposals. Never implement approval as a prompt instruction.

Start with read-only navigation and search. Add typing only for non-secret, approved fields. Keep submit, download, upload, external navigation, and unknown controls denied until each workflow has explicit evidence and an approval design.

## Observability

Ship the JSONL audit stream to the internal log system. Dashboard these counters by workflow and release digest:

- started, verified, verification failed, policy denied, timed out, and failed jobs;
- action count and elapsed time percentiles;
- denied action class and host;
- provider and browser errors;
- cleanup failures and orphan-container count.

Alert on any secret-scanner hit, undeclared-host attempt, cleanup failure, repeated provider failure, or verified-rate regression. Never use screenshot or full DOM capture as routine telemetry.

## Kill switch

The queue owner is the **Owner** of the global kill switch. Stop dispatch first, then terminate all active worker containers, then revoke provider secrets if data exposure is suspected. The worker has no inbound service and no long-lived browser state. Do not use `SIGKILL` on a bare-host worker because its detached Chrome subprocess can survive; production runs must use one container per job so container teardown removes all descendants.

A workflow-level kill switch removes that workflow from the dispatcher allowlist. A provider-level kill switch revokes its secret and sets `AVELI_EXTERNAL_DATA_APPROVED=false` in the next deployment.

## Incident response

1. Stop dispatch and terminate affected worker containers.
2. Preserve audit JSONL, release digest, job IDs, and provider request IDs. Do not collect credentials or full page content.
3. Revoke affected provider credentials.
4. Determine whether policy, provider, site behavior, prompt injection, or cleanup failed.
5. Add an offline regression and, when browser behavior matters, a real-Chrome regression.
6. Complete security review before re-enabling the workflow.

## Rollback

Rollback means switching the dispatcher to the prior approved image digest and prior workflow allowlist. Do not patch a running worker. Keep two known-good digests and their audit schema versions available. If the prior digest is incompatible with current job JSON, stop the workflow rather than translating requests through an unreviewed compatibility layer.

## Release gates

Code completion does not authorize production traffic. The release owner records every item below:

- named workflow and exact hosts;
- data-owner and security/privacy approval for both model providers;
- TypeSafe commercial availability, retention, residency, and incident terms;
- immutable image digest and passing offline, real-Chrome, deployment, and vulnerability checks;
- dashboard, alert, queue kill switch, secret revocation, rollback, and on-call Owner;
- at least **500** representative internal shadow/soak jobs over 14 days;
- at least **99%** independently verified success on those jobs;
- zero policy escapes, secret leaks, mutation retries, personal-profile attachments, or orphan browsers;
- reviewed failure samples for every non-verified status.

Until all items exist, keep the workflow disabled. External approvals and soak evidence cannot be satisfied by this repository.
