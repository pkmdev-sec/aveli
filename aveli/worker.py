"""One isolated internal job per process."""

import json
import os
import re
import signal
import sys
from collections.abc import Callable
from typing import Any, Mapping

from .audit import JsonlAuditSink
from .config import ProductionSettings
from .isolation import ChromeConfig, IsolatedChrome
from .job import JobResult, JobSpec, JobStatus

MAX_INPUT_BYTES = 64 * 1024


class WorkerDeadline(BaseException):
    pass


class WorkerCancelled(BaseException):
    pass


def _deadline_reached(*_args) -> None:
    raise WorkerDeadline("job hard deadline exceeded")


def _termination_requested(*_args) -> None:
    raise WorkerCancelled("worker terminated")


def execute(
    raw_job: Mapping[str, Any],
    environment: Mapping[str, str],
    *,
    chrome_factory: Callable[..., Any] = IsolatedChrome,
    runner_factory: Callable[..., Any] | None = None,
) -> JobResult:
    settings = ProductionSettings.from_env(environment)
    job = JobSpec.from_dict(raw_job)
    chrome_config = ChromeConfig.from_env(environment)
    safe_job_id = re.sub(r"[^a-zA-Z0-9_-]", "-", job.job_id)[:128]
    audit = JsonlAuditSink(settings.audit_dir / f"{safe_job_id}.jsonl")
    if runner_factory is None:
        from .runner import ProductionRunner

        runner_factory = ProductionRunner

    def network_denied(host: str) -> None:
        audit.emit("network_denied", {"job_id": job.job_id, "host": host})

    def cleanup_failed(reason: str) -> None:
        audit.emit("cleanup_failed", {"job_id": job.job_id, "reason": reason})

    with chrome_factory(
        job.job_id,
        chrome_config,
        allowed_hosts=job.allowed_hosts,
        on_network_denied=network_denied,
        on_cleanup_failure=cleanup_failed,
    ):
        return runner_factory(settings, audit_sink=audit).run(job)


def main() -> int:
    previous_term = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, _termination_requested)
    timer_started = False
    payload = None
    try:
        raw = (
            sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
            if hasattr(sys.stdin, "buffer")
            else sys.stdin.read(MAX_INPUT_BYTES + 1)
        )
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
            raise ValueError("Job input exceeds 64 KiB")
        payload = json.loads(raw)
        if hasattr(signal, "setitimer"):
            timeout = float(payload["timeout_seconds"])
            signal.signal(signal.SIGALRM, _deadline_reached)
            signal.setitimer(signal.ITIMER_REAL, timeout)
            timer_started = True
        result = execute(payload, os.environ)
        output = result.to_dict()
        exit_code = 0 if result.status is JobStatus.VERIFIED else 1
    except WorkerDeadline as error:
        output = {
            "job_id": payload.get("job_id") if isinstance(payload, dict) else None,
            "status": "timed_out",
            "reason": str(error),
        }
        exit_code = 1
    except WorkerCancelled as error:
        output = {
            "job_id": payload.get("job_id") if isinstance(payload, dict) else None,
            "status": "cancelled",
            "reason": str(error),
        }
        exit_code = 1
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        output = {"job_id": None, "status": "failed", "reason": f"Invalid job JSON or configuration: {error}"}
        exit_code = 2
    except Exception:
        output = {"job_id": None, "status": "failed", "reason": "worker execution failed"}
        exit_code = 1
    finally:
        if timer_started:
            signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGTERM, previous_term)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
