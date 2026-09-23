"""Production orchestration: policy before mutation, verification before success."""

import hashlib
import os
import time
from collections.abc import Callable
from typing import Any, Protocol

from .audit import AuditSink, NullAuditSink
from .config import ProductionSettings
from .job import (
    ActionPolicy,
    JobResult,
    JobSpec,
    JobStatus,
    PolicyAssessment,
    PolicyDisposition,
    PreparedAction,
    _public_url,
)


class AgentPort(Protocol):
    def snapshot(self) -> dict[str, Any]: ...
    def command(self, name: str, body: dict[str, Any] | None = None) -> dict[str, Any]: ...
    def proposed_action(self) -> dict[str, Any]: ...
    def close(self) -> None: ...


AgentFactory = Callable[[JobSpec], AgentPort]
ApprovalProvider = Callable[[JobSpec, PolicyAssessment, PreparedAction], bool]


class JobDeadlineReached(Exception):
    pass


class ProductionRunner:
    def __init__(
        self,
        settings: ProductionSettings,
        *,
        agent_factory: AgentFactory | None = None,
        approval_provider: ApprovalProvider | None = None,
        audit_sink: AuditSink | None = None,
    ):
        self.settings = settings
        self.agent_factory = agent_factory or self._create_agent
        self.approval_provider = approval_provider
        self.audit = audit_sink or NullAuditSink()
        self._active_deadline = None

    @staticmethod
    def _require_isolation(job: JobSpec) -> None:
        from .isolation import require_active_isolation

        isolation = require_active_isolation()
        if isolation.allowed_hosts != job.allowed_hosts:
            raise RuntimeError("Active isolation host policy does not match the job")

    def _create_agent(self, job: JobSpec) -> AgentPort:
        self._require_isolation(job)
        from .agent import Agent

        return Agent(
            job.url,
            job.goal,
            screenshots=False,
            max_actions=job.max_actions,
            mutation_observer=lambda action, fingerprint, text: self._audit_mutation(job, action, fingerprint, text),
        )

    def _audit_mutation(self, job, action, fingerprint, text) -> None:
        if self._active_deadline is not None and time.monotonic() >= self._active_deadline:
            raise JobDeadlineReached
        fields = PreparedAction.from_proposal("executing", fingerprint, action).audit_fields()
        if text is not None:
            fields.update(text_digest=hashlib.sha256(text.encode()).hexdigest(), text_length=len(text))
        self.audit.emit("browser_mutation_executing", {"job_id": job.job_id, **fields})

    def run(self, job: JobSpec) -> JobResult:
        if self._active_deadline is not None:
            raise RuntimeError("ProductionRunner cannot run concurrent jobs")
        self._require_isolation(job)
        os.environ.update(self.settings.provider_environment())
        started = time.monotonic()
        deadline = started + job.timeout_seconds
        self._active_deadline = deadline
        policy = ActionPolicy(job)
        agent: AgentPort | None = None
        self.audit.emit("job_started", {"job_id": job.job_id, "url": job.url})
        try:
            agent = self.agent_factory(job)
            state = agent.snapshot()
            if reason := policy.check_page(state["page"]["url"]):
                return self._result(job, JobStatus.POLICY_DENIED, reason, state, started)
            while state["status"] not in {"done", "blocked"}:
                if time.monotonic() >= deadline:
                    return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
                state = agent.command("predict", {})
                if time.monotonic() >= deadline:
                    return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
                proposal = agent.proposed_action()
                choice = proposal["choice"]
                if choice in {"DONE", "BLOCKED"}:
                    state = agent.command("act", {"fingerprint": proposal["fingerprint"]})
                    if time.monotonic() >= deadline:
                        return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
                    break
                action = proposal["action"]
                assessment = policy.assess(state["page"]["url"], action)
                prepared = PreparedAction.from_proposal(choice, proposal["fingerprint"], dict(action))
                self.audit.emit(
                    "policy_decision",
                    {
                        "job_id": job.job_id,
                        "action_class": assessment.action_class.value,
                        "disposition": assessment.disposition.value,
                        "reason": assessment.reason,
                    },
                )
                if assessment.disposition is PolicyDisposition.DENY:
                    return self._result(job, JobStatus.POLICY_DENIED, assessment.reason, state, started)
                if assessment.disposition is PolicyDisposition.REQUIRE_APPROVAL:
                    approved = bool(self.approval_provider and self.approval_provider(job, assessment, prepared))
                    if not approved:
                        return self._result(
                            job, JobStatus.APPROVAL_DENIED, "required action approval was not granted", state, started
                        )
                if time.monotonic() >= deadline:
                    return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
                current = agent.proposed_action()
                current_prepared = PreparedAction.from_proposal(
                    current["choice"], current["fingerprint"], dict(current["action"])
                )
                if current_prepared != prepared:
                    return self._result(job, JobStatus.POLICY_DENIED, "approved proposal changed", state, started)
                self.audit.emit("action_executing", {"job_id": job.job_id, **prepared.audit_fields()})
                state = agent.command("act", {"fingerprint": prepared.fingerprint})
                self.audit.emit(
                    "action_completed",
                    {
                        "job_id": job.job_id,
                        "action_class": assessment.action_class.value,
                        "actions_executed": len(state.get("history", [])),
                    },
                )
                if time.monotonic() >= deadline:
                    return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
                if reason := policy.check_page(state["page"]["url"]):
                    return self._result(job, JobStatus.POLICY_DENIED, reason, state, started)
            if state["status"] == "blocked":
                return self._result(job, JobStatus.BLOCKED, "agent reported that it could not progress", state, started)
            verification = job.verification.verify(state["page"])
            status = JobStatus.VERIFIED if verification.passed else JobStatus.VERIFICATION_FAILED
            self.audit.emit(
                "verification",
                {"job_id": job.job_id, "passed": verification.passed, "reason": verification.reason},
            )
            return self._result(job, status, verification.reason, state, started, verification)
        except JobDeadlineReached:
            state = agent.snapshot() if agent else {}
            return self._result(job, JobStatus.TIMED_OUT, "job deadline reached", state, started)
        except Exception as error:
            state = agent.snapshot() if agent else {}
            self.audit.emit("job_error", {"job_id": job.job_id, "error_type": type(error).__name__})
            return self._result(job, JobStatus.FAILED, "job execution failed", state, started)
        finally:
            self._active_deadline = None
            if agent:
                agent.close()

    def _result(self, job, status, reason, state, started, verification=None) -> JobResult:
        page = state.get("page", {})
        result = JobResult(
            job_id=job.job_id,
            status=status,
            reason=reason,
            final_url=_public_url(page.get("url")),
            actions_executed=len(state.get("history", [])),
            elapsed_ms=round((time.monotonic() - started) * 1000),
            verification=verification,
        )
        self.audit.emit("job_finished", result.to_dict())
        return result
