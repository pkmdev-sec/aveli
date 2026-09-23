"""Static deployment invariants that reviewers and CI can rerun."""

from pathlib import Path


def require(text, needle, source):
    if needle not in text:
        raise AssertionError(f"{source} is missing {needle!r}")


def main():
    docker = Path("deploy/Dockerfile").read_text()
    workflow = Path(".github/workflows/ci.yml").read_text()
    docs = Path("docs/internal-production.md").read_text()
    required_docker_values = (
        "USER 10001:10001",
        "uv sync --frozen --no-dev",
        'ENTRYPOINT ["aveli-internal-worker"]',
        "HEALTHCHECK",
    )
    for value in required_docker_values:
        require(docker, value, "deploy/Dockerfile")
    if "--no-sandbox" in docker:
        raise AssertionError("Chrome sandbox must not be disabled")
    require(workflow, "check_network_isolation.py", ".github/workflows/ci.yml")
    require(workflow, "docker image inspect", ".github/workflows/ci.yml")
    for job in ("offline:", "browser:", "container:"):
        require(workflow, job, ".github/workflows/ci.yml")
    for control in ("Kill switch", "Rollback", "Incident response", "Redaction", "500", "99%", "Owner"):
        require(docs, control, "docs/internal-production.md")
    print("DEPLOYMENT_CHECK_PASS")


if __name__ == "__main__":
    main()
