"""Fail when the locked Python environment has known OSV vulnerabilities."""

import json
import tomllib
import urllib.request
from pathlib import Path


def main():
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    packages = [
        package for package in lock["package"] if package.get("version") and package.get("source", {}).get("registry")
    ]
    queries = [
        {"package": {"name": package["name"], "ecosystem": "PyPI"}, "version": package["version"]}
        for package in packages
    ]
    request = urllib.request.Request(
        "https://api.osv.dev/v1/querybatch",
        data=json.dumps({"queries": queries}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        results = json.load(response)["results"]
    findings = [
        (package["name"], package["version"], [item["id"] for item in result.get("vulns", [])])
        for package, result in zip(packages, results, strict=True)
        if result.get("vulns")
    ]
    if findings:
        for name, version, identifiers in findings:
            print(f"{name}=={version}: {', '.join(identifiers)}")
        raise SystemExit(1)
    print(f"NO_RUNTIME_VULNERABILITIES ({len(packages)} locked registry packages checked)")
    print("NO_LOCKED_VULNERABILITIES")


if __name__ == "__main__":
    main()
