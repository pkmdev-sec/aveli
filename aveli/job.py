"""Immutable job, policy, verification, and result types."""

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
from urllib.parse import urljoin, urlparse


class ActionClass(str, Enum):
    NAVIGATE = "navigate"
    INTERACT = "interact"
    TYPE_TEXT = "type_text"
    SELECT = "select"
    SUBMIT = "submit"
    DOWNLOAD = "download"
    SCROLL = "scroll"
    WAIT = "wait"
    UNKNOWN = "unknown"


class PolicyDisposition(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


class JobStatus(str, Enum):
    VERIFIED = "verified"
    VERIFICATION_FAILED = "verification_failed"
    BLOCKED = "blocked"
    POLICY_DENIED = "policy_denied"
    APPROVAL_DENIED = "approval_denied"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"
    FAILED = "failed"


def _host(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URLs must be HTTP(S), include a host, and contain no credentials")
    loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if loopback:
        raise ValueError("Production job URLs cannot target loopback services")
    if parsed.scheme == "http":
        raise ValueError("Job URLs must use HTTPS")
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("URL port is invalid") from None
    if port not in {None, 443}:
        raise ValueError("Job URLs must use the default HTTPS port")
    return parsed.hostname.rstrip(".").lower()


def _strings(value: Any, name: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise ValueError(f"{name} must not be empty")
    return tuple(item.strip() for item in value)


@dataclass(frozen=True)
class VerificationOutcome:
    passed: bool
    reason: str
    checks: tuple[str, ...]


@dataclass(frozen=True)
class VerificationSpec:
    url_prefix: str | None
    title_contains: tuple[str, ...]
    required_text: tuple[str, ...]
    forbidden_text: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "VerificationSpec":
        if not isinstance(raw, Mapping):
            raise ValueError("verification must be an object")
        unknown = set(raw) - {"url_prefix", "title_contains", "required_text", "forbidden_text"}
        if unknown:
            raise ValueError(f"Unknown verification fields: {sorted(unknown)}")
        prefix = raw.get("url_prefix")
        if prefix is not None:
            if not isinstance(prefix, str) or not prefix.strip():
                raise ValueError("verification.url_prefix must be a non-empty string")
            _host(prefix)
            prefix = prefix.strip()
        titles = _strings(raw.get("title_contains", []), "verification.title_contains")
        required = _strings(raw.get("required_text", []), "verification.required_text")
        forbidden = _strings(raw.get("forbidden_text", []), "verification.forbidden_text")
        if not prefix and not titles and not required:
            raise ValueError("verification needs positive URL, title, or page-text evidence")
        return cls(prefix, titles, required, forbidden)

    def verify(self, page: Mapping[str, Any]) -> VerificationOutcome:
        url = str(page.get("url", ""))
        title = str(page.get("title", ""))
        text = str(page.get("text", ""))
        checks: list[str] = []
        if self.url_prefix:
            if not url.startswith(self.url_prefix):
                return VerificationOutcome(False, "final URL does not match the required prefix", tuple(checks))
            checks.append("url_prefix")
        for index, expected in enumerate(self.title_contains):
            if expected not in title:
                return VerificationOutcome(False, "required title text is missing", tuple(checks))
            checks.append(f"title_contains:{index}")
        for index, expected in enumerate(self.required_text):
            if expected not in text:
                return VerificationOutcome(False, "required page text is missing", tuple(checks))
            checks.append(f"required_text:{index}")
        for index, forbidden in enumerate(self.forbidden_text):
            if forbidden in text:
                return VerificationOutcome(False, "forbidden page text is present", tuple(checks))
            checks.append(f"forbidden_text_absent:{index}")
        return VerificationOutcome(True, "all independent checks passed", tuple(checks))


@dataclass(frozen=True)
class JobSpec:
    schema_version: int
    job_id: str
    url: str
    goal: str
    allowed_hosts: frozenset[str]
    allowed_actions: frozenset[ActionClass]
    approval_required_actions: frozenset[ActionClass]
    verification: VerificationSpec
    timeout_seconds: float
    max_actions: int

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "JobSpec":
        if not isinstance(raw, Mapping):
            raise ValueError("job must be an object")
        expected = {
            "schema_version",
            "job_id",
            "url",
            "goal",
            "allowed_hosts",
            "allowed_actions",
            "approval_required_actions",
            "verification",
            "timeout_seconds",
            "max_actions",
        }
        unknown = set(raw) - expected
        missing = expected - set(raw)
        if unknown or missing:
            raise ValueError(f"Invalid job fields; missing={sorted(missing)}, unknown={sorted(unknown)}")
        if raw["schema_version"] != 1:
            raise ValueError("schema_version must be 1")
        job_id = raw["job_id"]
        goal = raw["goal"]
        url = raw["url"]
        if not isinstance(job_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", job_id):
            raise ValueError("job_id must contain only letters, digits, underscores, and hyphens")
        if not isinstance(goal, str) or not goal.strip() or len(goal) > 2000:
            raise ValueError("goal must contain 1-2000 characters")
        if not isinstance(url, str):
            raise ValueError("url must be a string")
        initial_host = _host(url)
        hosts = frozenset(
            host.rstrip(".").lower() for host in _strings(raw["allowed_hosts"], "allowed_hosts", allow_empty=False)
        )
        if initial_host not in hosts:
            raise ValueError("The initial URL host must be explicitly allowed")
        if any("/" in host or ":" in host or _host(f"https://{host}") != host for host in hosts):
            raise ValueError("allowed_hosts entries must be bare hostnames")
        try:
            allowed = frozenset(
                ActionClass(value) for value in _strings(raw["allowed_actions"], "allowed_actions", allow_empty=False)
            )
            approvals = frozenset(
                ActionClass(value) for value in _strings(raw["approval_required_actions"], "approval_required_actions")
            )
        except ValueError as error:
            raise ValueError(f"Unknown action class: {error}") from None
        if ActionClass.UNKNOWN in allowed | approvals:
            raise ValueError("unknown cannot be configured as an allowed action class")
        if ActionClass.TYPE_TEXT in approvals:
            raise ValueError("type_text approval is unsupported; deny it or allow only an approved non-secret workflow")
        if allowed & approvals:
            raise ValueError("An action class cannot be both automatic and approval-required")
        timeout = raw["timeout_seconds"]
        max_actions = raw["max_actions"]
        if type(timeout) not in {int, float} or not 1 <= timeout <= 600:
            raise ValueError("timeout_seconds must be between 1 and 600")
        if type(max_actions) is not int or not 1 <= max_actions <= 60:
            raise ValueError("max_actions must be between 1 and 60")
        return cls(
            1,
            job_id.strip(),
            url.strip(),
            goal.strip(),
            hosts,
            allowed,
            approvals,
            VerificationSpec.from_dict(raw["verification"]),
            float(timeout),
            max_actions,
        )


@dataclass(frozen=True)
class PolicyAssessment:
    disposition: PolicyDisposition
    action_class: ActionClass
    reason: str


class ActionPolicy:
    def __init__(self, job: JobSpec):
        self.job = job

    def check_page(self, url: str) -> str | None:
        try:
            host = _host(url)
        except ValueError as error:
            return str(error)
        if host not in self.job.allowed_hosts:
            return f"Page host {host!r} is not allowed"
        return None

    def assess(self, page_url: str, action: Mapping[str, Any]) -> PolicyAssessment:
        page_error = self.check_page(page_url)
        action_class = classify_action(action)
        if page_error:
            return PolicyAssessment(PolicyDisposition.DENY, action_class, page_error)
        if action_class is ActionClass.UNKNOWN:
            return PolicyAssessment(PolicyDisposition.DENY, action_class, "unknown action kind")
        href = action.get("href")
        if action_class is ActionClass.NAVIGATE and isinstance(href, str):
            destination = urljoin(page_url, href)
            destination_error = self.check_page(destination)
            if destination_error:
                return PolicyAssessment(PolicyDisposition.DENY, action_class, destination_error)
        if action_class in self.job.allowed_actions:
            return PolicyAssessment(PolicyDisposition.ALLOW, action_class, "action class is pre-approved")
        if action_class in self.job.approval_required_actions:
            return PolicyAssessment(PolicyDisposition.REQUIRE_APPROVAL, action_class, "action requires approval")
        return PolicyAssessment(PolicyDisposition.DENY, action_class, "action class is not allowed")


def classify_action(action: Mapping[str, Any]) -> ActionClass:
    kind = action.get("kind")
    if kind == "fill":
        return ActionClass.TYPE_TEXT
    if kind == "select":
        return ActionClass.SELECT
    if kind == "scroll":
        return ActionClass.SCROLL
    if kind == "wait":
        return ActionClass.WAIT
    if kind == "click":
        if action.get("effect") == "submit":
            return ActionClass.SUBMIT
        if action.get("effect") == "download":
            return ActionClass.DOWNLOAD
        if str(action.get("tag", "")).lower() == "a" and action.get("href"):
            return ActionClass.NAVIGATE
        return ActionClass.INTERACT
    return ActionClass.UNKNOWN


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True)
class PreparedAction:
    """Immutable commitment approved before a browser mutation."""

    choice: str
    fingerprint: str
    action_class: ActionClass
    kind: str
    node: int | None
    option_node: int | None
    href: str | None = field(repr=False)
    label: str = field(repr=False)
    value: str | None = field(repr=False)

    @classmethod
    def from_proposal(cls, choice: str, fingerprint: str, action: Mapping[str, Any]) -> "PreparedAction":
        value = action.get("value")
        return cls(
            choice=choice,
            fingerprint=fingerprint,
            action_class=classify_action(action),
            kind=str(action.get("kind", "")),
            node=action.get("node") if type(action.get("node")) is int else None,
            option_node=action.get("option_node") if type(action.get("option_node")) is int else None,
            href=action.get("href") if isinstance(action.get("href"), str) else None,
            label=str(action.get("label", "")),
            value=str(value) if value is not None else None,
        )

    def audit_fields(self) -> dict[str, Any]:
        return {
            "action_class": self.action_class.value,
            "kind": self.kind,
            "node": self.node,
            "option_node": self.option_node,
            "href_digest": _digest(self.href) if self.href else None,
            "label_digest": _digest(self.label),
            "value_digest": _digest(self.value) if self.value is not None else None,
            "value_length": len(self.value) if self.value is not None else None,
            "page_fingerprint": self.fingerprint,
        }


def _public_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        return None
    try:
        parsed_port = parsed.port
    except ValueError:
        return None
    port = f":{parsed_port}" if parsed_port and parsed_port != 443 else ""
    return f"{parsed.scheme}://{parsed.hostname}{port}/<redacted>"


@dataclass(frozen=True)
class JobResult:
    job_id: str
    status: JobStatus
    reason: str
    final_url: str | None
    actions_executed: int
    elapsed_ms: int
    verification: VerificationOutcome | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "final_url", _public_url(self.final_url))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "job_id": self.job_id,
            "status": self.status.value,
            "reason": self.reason,
            "final_url": self.final_url,
            "actions_executed": self.actions_executed,
            "elapsed_ms": self.elapsed_ms,
            "verification": None
            if self.verification is None
            else {
                "passed": self.verification.passed,
                "reason": self.verification.reason,
                "checks": list(self.verification.checks),
            },
        }
