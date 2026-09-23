"""Scan tracked and candidate source files for credential-shaped literals."""

import re
import subprocess
from pathlib import Path

PATTERNS = (
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"(?:TYPESAFE_API_KEY|TEXT_MODEL_API_KEY)[ \t]*=[ \t]*[^\s#]{8,}"),
    re.compile(rb"(?i)authorization:\s*bearer\s+[A-Za-z0-9._-]{16,}"),
)


def main():
    output = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    findings = []
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        path = Path(raw_path.decode())
        if path.parts[0] in {"dist", ".venv"} or not path.is_file():
            continue
        content = path.read_bytes()
        if any(pattern.search(content) for pattern in PATTERNS):
            findings.append(str(path))
    if findings:
        raise SystemExit("Credential-shaped literals found in: " + ", ".join(findings))
    print("NO_CREDENTIALS_FOUND")


if __name__ == "__main__":
    main()
