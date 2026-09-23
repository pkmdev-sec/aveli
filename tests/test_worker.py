import io
import json
import stat

from aveli.job import JobResult, JobStatus, VerificationOutcome
from aveli.worker import execute, main


def environment(tmp_path):
    chrome = tmp_path / "chrome"
    chrome.touch()
    return {
        "TYPESAFE_API_KEY": "typesafe-secret",
        "TYPESAFE_MODEL": "jev-1.13.0",
        "TEXT_MODEL_API_KEY": "text-secret",
        "TEXT_MODEL_BASE_URL": "https://models.example/v1",
        "TEXT_MODEL": "mercury-2.5",
        "AVELI_EXTERNAL_DATA_APPROVED": "true",
        "AVELI_AUDIT_DIR": str(tmp_path / "audit"),
        "AVELI_CHROME_PATH": str(chrome),
    }


def payload():
    return {
        "schema_version": 1,
        "job_id": "job-safe-name",
        "url": "https://internal.example/start",
        "goal": "Find the result",
        "allowed_hosts": ["internal.example"],
        "allowed_actions": ["navigate"],
        "approval_required_actions": ["submit"],
        "verification": {"required_text": ["Success"]},
        "timeout_seconds": 30,
        "max_actions": 10,
    }


class FakeChrome:
    last_kwargs = None

    def __init__(self, *_args, **kwargs):
        self.entered = False
        FakeChrome.last_kwargs = kwargs

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *_args):
        self.entered = False


class FakeRunner:
    def __init__(self, settings, audit_sink=None):
        self.audit = audit_sink

    def run(self, job):
        self.audit.emit(
            "test_event",
            {
                "job_id": job.job_id,
                "api_key": "must-not-leak",
                "reason": "token=also-secret Bearer bearer-secret-material",
            },
        )
        return JobResult(
            job.job_id,
            JobStatus.VERIFIED,
            "ok",
            "https://internal.example/result",
            1,
            10,
            VerificationOutcome(True, "passed", ("text:Success",)),
        )


def test_execute_uses_isolation_and_writes_redacted_audit(tmp_path):
    result = execute(payload(), environment(tmp_path), chrome_factory=FakeChrome, runner_factory=FakeRunner)
    assert result.status is JobStatus.VERIFIED
    assert FakeChrome.last_kwargs["allowed_hosts"] == frozenset({"internal.example"})
    audits = list((tmp_path / "audit").glob("*.jsonl"))
    assert len(audits) == 1
    content = audits[0].read_text()
    assert "must-not-leak" not in content
    assert "also-secret" not in content
    assert "bearer-secret-material" not in content
    assert "<redacted>" in content
    assert "/" not in audits[0].stem
    assert stat.S_IMODE(audits[0].stat().st_mode) == 0o600


def test_main_returns_machine_readable_failure_for_invalid_json(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr("sys.stdin", io.StringIO("not-json"))
    monkeypatch.setattr("sys.stdout", output)
    assert main() == 2
    response = json.loads(output.getvalue())
    assert response["status"] == "failed"
    assert "JSON" in response["reason"]
