import pytest

from aveli.job import (
    ActionClass,
    ActionPolicy,
    JobSpec,
    PolicyDisposition,
    VerificationSpec,
)


def payload():
    return {
        "schema_version": 1,
        "job_id": "trip-search-001",
        "url": "https://travel.example/search",
        "goal": "Find the approved route without booking it.",
        "allowed_hosts": ["travel.example"],
        "allowed_actions": ["navigate", "interact", "type_text", "scroll", "wait"],
        "approval_required_actions": ["submit"],
        "verification": {
            "url_prefix": "https://travel.example/results",
            "required_text": ["Approved route"],
            "forbidden_text": ["No results"],
        },
        "timeout_seconds": 90,
        "max_actions": 30,
    }


def test_job_spec_parses_to_immutable_validated_types():
    job = JobSpec.from_dict(payload())
    assert job.allowed_hosts == frozenset({"travel.example"})
    assert ActionClass.SUBMIT in job.approval_required_actions
    with pytest.raises(AttributeError):
        job.goal = "changed"


@pytest.mark.parametrize(
    "change",
    [
        lambda p: p.update(url="file:///tmp/secret"),
        lambda p: p.update(allowed_hosts=["other.example"]),
        lambda p: p.update(allowed_actions=[]),
        lambda p: p.update(verification={}),
        lambda p: p.update(timeout_seconds=0),
        lambda p: p.update(max_actions=61),
    ],
)
def test_job_spec_rejects_unsafe_or_unverifiable_inputs(change):
    raw = payload()
    change(raw)
    with pytest.raises(ValueError):
        JobSpec.from_dict(raw)


def test_policy_classifies_and_restricts_hosts_and_actions():
    job = JobSpec.from_dict(payload())
    policy = ActionPolicy(job)

    navigation = {"kind": "click", "tag": "a", "href": "https://travel.example/results", "label": "Results"}
    assert policy.assess(job.url, navigation).disposition is PolicyDisposition.ALLOW

    cross_host = {**navigation, "href": "https://evil.example/collect"}
    assert policy.assess(job.url, cross_host).disposition is PolicyDisposition.DENY

    submit = {"kind": "click", "effect": "submit", "label": "Search"}
    assessment = policy.assess(job.url, submit)
    assert assessment.action_class is ActionClass.SUBMIT
    assert assessment.disposition is PolicyDisposition.REQUIRE_APPROVAL

    unknown_click = {"kind": "click", "tag": "button", "label": "Delete account"}
    assert policy.assess(job.url, unknown_click).action_class is ActionClass.INTERACT


def test_verification_requires_all_declared_evidence():
    verifier = VerificationSpec.from_dict(payload()["verification"])
    passed = verifier.verify(
        {
            "url": "https://travel.example/results/42",
            "title": "Results",
            "text": "Approved route is available",
        }
    )
    assert passed.passed

    failed = verifier.verify(
        {
            "url": "https://travel.example/results/42",
            "title": "Results",
            "text": "Approved route - No results",
        }
    )
    assert not failed.passed
    assert "forbidden page text" in failed.reason


def test_unknown_action_kind_fails_closed():
    spec = JobSpec.from_dict(payload())
    result = ActionPolicy(spec).assess(spec.url, {"kind": "model_invented", "label": "unsafe"})
    assert result.disposition is PolicyDisposition.DENY
    assert result.action_class is ActionClass.UNKNOWN


def test_unsafe_job_id_is_rejected():
    with pytest.raises(ValueError, match="job_id"):
        raw = payload()
        raw["job_id"] = "../../audit"
        JobSpec.from_dict(raw)


def test_loopback_and_non_default_ports_are_rejected():
    for url in ("http://127.0.0.1:8080/", "https://localhost/", "https://travel.example:8443/"):
        raw = payload()
        raw["url"] = url
        raw["allowed_hosts"] = [url.split("//", 1)[1].split(":", 1)[0].rstrip("/")]
        with pytest.raises(ValueError):
            JobSpec.from_dict(raw)


def test_type_text_cannot_use_the_approval_path_without_exact_preparation():
    raw = payload()
    raw["allowed_actions"].remove("type_text")
    raw["approval_required_actions"].append("type_text")
    with pytest.raises(ValueError, match="type_text approval is unsupported"):
        JobSpec.from_dict(raw)


def test_verification_output_does_not_repeat_expected_secrets():
    verifier = VerificationSpec.from_dict({"required_text": ["private-verification-secret"]})
    outcome = verifier.verify({"url": "https://travel.example/", "title": "", "text": "missing"})
    assert "private-verification-secret" not in outcome.reason
    assert all("private-verification-secret" not in check for check in outcome.checks)


def test_download_is_not_misclassified_as_navigation():
    spec = JobSpec.from_dict(payload())
    result = ActionPolicy(spec).assess(
        spec.url, {"kind": "click", "effect": "download", "tag": "a", "href": "https://travel.example/file"}
    )
    assert result.action_class is ActionClass.DOWNLOAD
    assert result.disposition is PolicyDisposition.DENY


def test_job_and_result_contracts_are_versioned():
    raw = payload()
    raw.pop("schema_version")
    with pytest.raises(ValueError):
        JobSpec.from_dict(raw)

    from aveli.job import JobResult, JobStatus

    result = JobResult("job-1", JobStatus.FAILED, "failed", "https://travel.example/private?token=x", 0, 1)
    assert result.to_dict()["schema_version"] == 1
    assert result.final_url == "https://travel.example/<redacted>"
