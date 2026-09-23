from collections import deque

import pytest

from aveli.config import ProductionSettings
from aveli.job import JobSpec, JobStatus
from aveli.runner import ProductionRunner


@pytest.fixture(autouse=True)
def active_isolation(monkeypatch):
    from types import SimpleNamespace

    monkeypatch.setattr(
        "aveli.isolation.require_active_isolation",
        lambda: SimpleNamespace(allowed_hosts=frozenset({"internal.example"})),
    )


def settings():
    return ProductionSettings(
        typesafe_api_key="a",
        typesafe_model="jev-1.13.0",
        text_model_api_key="b",
        text_model_base_url="https://models.example/v1",
        text_model="text-2.5",
        text_model_reasoning="none",
        external_data_approved=True,
    )


def job(**changes):
    raw = {
        "schema_version": 1,
        "job_id": "job-1",
        "url": "https://internal.example/start",
        "goal": "Find the result",
        "allowed_hosts": ["internal.example"],
        "allowed_actions": ["navigate", "wait"],
        "approval_required_actions": ["submit"],
        "verification": {"url_prefix": "https://internal.example/result", "required_text": ["Success"]},
        "timeout_seconds": 30,
        "max_actions": 10,
    }
    raw.update(changes)
    return JobSpec.from_dict(raw)


class FakeAgent:
    def __init__(self, proposals, pages=None):
        self.proposals = deque(proposals)
        self.pages = deque(pages or [])
        self.current = None
        self.act_calls = 0
        self.closed = False
        self.state = {
            "status": "ready",
            "page": {"url": "https://internal.example/start", "title": "Start", "text": "Start", "fingerprint": "f0"},
            "history": [],
            "elapsed_ms": 0,
        }

    def snapshot(self):
        return self.state

    def command(self, name, body=None):
        if name == "predict":
            self.current = self.proposals.popleft()
            self.state["status"] = "predicted"
        elif name == "act":
            selected = self.current["choice"]
            if selected == "DONE":
                self.state["status"] = "done"
            elif selected == "BLOCKED":
                self.state["status"] = "blocked"
            else:
                self.act_calls += 1
                self.state["history"].append({"action": self.current["action"]["label"]})
                if self.pages:
                    self.state["page"] = self.pages.popleft()
                self.state["status"] = "ready"
        return self.state

    def proposed_action(self):
        return self.current

    def close(self):
        self.closed = True


def proposal(action):
    return {"choice": "e1", "action": action, "fingerprint": "f0"}


def terminal(name):
    return {"choice": name, "action": None, "fingerprint": "f0"}


def result_page(text="Success", url="https://internal.example/result"):
    return {"url": url, "title": "Result", "text": text, "fingerprint": "f1"}


def test_policy_denial_stops_before_browser_mutation():
    fake = FakeAgent([proposal({"kind": "click", "tag": "button", "label": "Delete"})])
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.POLICY_DENIED
    assert fake.act_calls == 0
    assert fake.closed


def test_cross_host_navigation_is_denied_before_browser_mutation():
    action = {"kind": "click", "tag": "a", "href": "https://evil.example/", "label": "Leave"}
    fake = FakeAgent([proposal(action)])
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.POLICY_DENIED
    assert fake.act_calls == 0


def test_approval_required_action_denies_without_provider():
    action = {"kind": "click", "effect": "submit", "tag": "button", "label": "Submit"}
    fake = FakeAgent([proposal(action)])
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.APPROVAL_DENIED
    assert fake.act_calls == 0


def test_approved_action_executes_then_independent_verification_passes():
    action = {"kind": "click", "effect": "submit", "tag": "button", "label": "Submit"}
    fake = FakeAgent([proposal(action), terminal("DONE")], pages=[result_page()])
    runner = ProductionRunner(settings(), agent_factory=lambda _: fake, approval_provider=lambda *_: True)
    result = runner.run(job())
    assert result.status is JobStatus.VERIFIED
    assert result.verification and result.verification.passed
    assert fake.act_calls == 1


def test_model_done_is_not_success_when_verification_fails():
    fake = FakeAgent([terminal("DONE")])
    fake.state["page"] = result_page(text="Still loading")
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.VERIFICATION_FAILED
    assert result.verification and not result.verification.passed


def test_post_action_cross_host_redirect_stops_job():
    action = {"kind": "click", "tag": "a", "href": "/result", "label": "Result"}
    fake = FakeAgent([proposal(action)], pages=[result_page(url="https://evil.example/collect")])
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.POLICY_DENIED
    assert fake.act_calls == 1


class RecordingAudit:
    def __init__(self):
        self.events = []

    def emit(self, event, fields):
        self.events.append(event)


def test_execution_intent_is_audited_before_browser_mutation():
    audit = RecordingAudit()
    action = {"kind": "click", "tag": "a", "href": "/result", "label": "Result"}
    fake = FakeAgent([proposal(action), terminal("DONE")], pages=[result_page()])
    original_command = fake.command

    def command(name, body=None):
        if name == "act" and fake.current["choice"] == "e1":
            assert audit.events[-1] == "action_executing"
        return original_command(name, body)

    fake.command = command
    result = ProductionRunner(settings(), audit_sink=audit, agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.VERIFIED
    assert audit.events.index("action_executing") < audit.events.index("action_completed")


def test_slow_prediction_cannot_mutate_after_deadline(monkeypatch):
    fake = FakeAgent([proposal({"kind": "wait", "label": "Wait"})])
    ticks = iter([0.0, 0.0, 31.0, 31.0])
    monkeypatch.setattr("aveli.runner.time.monotonic", lambda: next(ticks))
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert result.status is JobStatus.TIMED_OUT
    assert fake.act_calls == 0


def test_hard_worker_deadline_escapes_runner_and_still_closes_agent():
    from aveli.worker import WorkerDeadline

    class DeadlineAgent(FakeAgent):
        def command(self, name, body=None):
            raise WorkerDeadline("deadline")

    fake = DeadlineAgent([terminal("DONE")])
    with pytest.raises(WorkerDeadline):
        ProductionRunner(settings(), agent_factory=lambda _: fake).run(job())
    assert fake.closed


def test_default_production_agent_requires_active_isolation(monkeypatch):
    def missing():
        raise RuntimeError("ProductionRunner requires an active IsolatedChrome context")

    monkeypatch.setattr("aveli.isolation.require_active_isolation", missing)
    runner = ProductionRunner(settings())
    with pytest.raises(RuntimeError, match="active IsolatedChrome"):
        runner._create_agent(job())


def test_approval_receives_frozen_exact_action():
    from dataclasses import FrozenInstanceError

    action = {"kind": "click", "effect": "submit", "tag": "button", "node": 42, "label": "Submit"}
    fake = FakeAgent([proposal(action), terminal("DONE")], pages=[result_page()])
    seen = []

    def approve(_job, _assessment, prepared):
        seen.append(prepared)
        with pytest.raises(FrozenInstanceError):
            prepared.node = 99
        return True

    result = ProductionRunner(settings(), agent_factory=lambda _: fake, approval_provider=approve).run(job())
    assert result.status is JobStatus.VERIFIED
    assert seen[0].node == 42 and seen[0].fingerprint == "f0"


def test_public_result_url_removes_path_query_and_fragment():
    fake = FakeAgent([terminal("DONE")])
    fake.state["page"] = result_page(url="https://internal.example/reset/private?token=secret#code")
    custom_job = job(verification={"required_text": ["Success"]})
    result = ProductionRunner(settings(), agent_factory=lambda _: fake).run(custom_job)
    assert result.status is JobStatus.VERIFIED
    assert result.final_url == "https://internal.example/<redacted>"
    assert "secret" not in str(result.to_dict())


def test_active_isolation_hosts_must_exactly_match_job(monkeypatch):
    from types import SimpleNamespace

    monkeypatch.setattr(
        "aveli.isolation.require_active_isolation",
        lambda: SimpleNamespace(allowed_hosts=frozenset({"other.example"})),
    )
    with pytest.raises(RuntimeError, match="host policy does not match"):
        ProductionRunner(settings())._create_agent(job())


def test_final_pre_mutation_hook_enforces_deadline(monkeypatch):
    from aveli.runner import JobDeadlineReached

    runner = ProductionRunner(settings())
    runner._active_deadline = 10.0
    monkeypatch.setattr("aveli.runner.time.monotonic", lambda: 10.0)
    with pytest.raises(JobDeadlineReached):
        runner._audit_mutation(job(), {"kind": "click", "node": 1}, "fingerprint", None)
