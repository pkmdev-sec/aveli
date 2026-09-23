"""Offline smoke check for worker policy denial and audit redaction."""

import json
import tempfile
from pathlib import Path

from aveli.runner import ProductionRunner
from aveli.worker import execute


class NoopChrome:
    def __init__(self, *_args, **_kwargs):
        pass

    def __enter__(self):
        from aveli import isolation

        self.previous = isolation._ACTIVE_ISOLATION
        isolation._ACTIVE_ISOLATION = type("OfflineIsolation", (), {"allowed_hosts": frozenset({"internal.example"})})()
        return self

    def __exit__(self, *_args):
        from aveli import isolation

        isolation._ACTIVE_ISOLATION = self.previous


class DeniedAgent:
    def __init__(self):
        self.acts = 0
        self.state = {
            "status": "ready",
            "history": [],
            "elapsed_ms": 0,
            "page": {"url": "https://internal.example/start", "title": "Start", "text": "Start", "fingerprint": "f"},
        }

    def snapshot(self):
        return self.state

    def command(self, name, body=None):
        if name == "predict":
            self.state["status"] = "predicted"
        elif name == "act":
            self.acts += 1
        return self.state

    def proposed_action(self):
        return {"choice": "e1", "fingerprint": "f", "action": {"kind": "click", "tag": "button", "label": "Delete"}}

    def close(self):
        pass


def main():
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        chrome = root / "chrome"
        chrome.touch()
        environment = {
            "TYPESAFE_API_KEY": "redacted-typesafe",
            "TYPESAFE_MODEL": "jev-1.13.0",
            "TEXT_MODEL_API_KEY": "redacted-text",
            "TEXT_MODEL_BASE_URL": "https://models.example/v1",
            "TEXT_MODEL": "text-2.5",
            "AVELI_EXTERNAL_DATA_APPROVED": "true",
            "AVELI_AUDIT_DIR": str(root / "audit"),
            "AVELI_CHROME_PATH": str(chrome),
        }
        job = {
            "schema_version": 1,
            "job_id": "offline-policy-smoke",
            "url": "https://internal.example/start",
            "goal": "Do not execute the disallowed action",
            "allowed_hosts": ["internal.example"],
            "allowed_actions": ["wait"],
            "approval_required_actions": [],
            "verification": {"required_text": ["never reached"]},
            "timeout_seconds": 10,
            "max_actions": 2,
        }
        agent = DeniedAgent()

        def runner_factory(settings, audit_sink):
            return ProductionRunner(settings, audit_sink=audit_sink, agent_factory=lambda _: agent)

        result = execute(job, environment, chrome_factory=NoopChrome, runner_factory=runner_factory)
        audit = next((root / "audit").glob("*.jsonl")).read_text()
        assert result.status.value == "policy_denied"
        assert agent.acts == 0
        assert "redacted-typesafe" not in audit and "redacted-text" not in audit
        print(json.dumps(result.to_dict(), sort_keys=True))
        print("WORKER_SMOKE_PASS")


if __name__ == "__main__":
    main()
