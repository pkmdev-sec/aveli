# Gates: production release authorization

Scope: Non-code evidence required before any internal production traffic. Repository implementation cannot satisfy these gates.

- [ ] R1: The data owner and security/privacy reviewer approve sending declared page data to TypeSafe and the configured text-model provider.
  EVIDENCE: blocked — no approval artifact supplied.

- [ ] R2: Procurement/legal approve TypeSafe commercial availability, retention, residency, security, and incident terms.
  EVIDENCE: blocked — external provider terms are not in this repository.

- [ ] R3: A named workflow owner supplies the exact page and network host allowlist, approval design, dashboard, alerts, queue kill switch, rollback digest, and on-call owner.
  EVIDENCE: blocked — no target workflow was named.

- [ ] R4: The release candidate completes at least 500 representative shadow/soak jobs over 14 days with at least 99% independently verified success and zero critical safety failures.
  EVIDENCE: blocked — soak traffic has not run.

- [ ] R5: Hosted CI builds and tests the immutable container, and the release manifest records its digest.
  EVIDENCE: blocked — workflow exists, but this branch has not been pushed and the local Docker daemon was unavailable.
