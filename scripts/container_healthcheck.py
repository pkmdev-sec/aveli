"""Container preflight without model calls or browser startup."""

import os
from pathlib import Path

from aveli.isolation import ChromeConfig


def main():
    config = ChromeConfig.from_env(os.environ)
    if not os.access(config.executable, os.X_OK):
        raise SystemExit("Chrome is not executable")
    audit_dir = Path(os.environ["AVELI_AUDIT_DIR"])
    runtime_root = Path(os.environ["AVELI_RUNTIME_ROOT"])
    if not all(path.exists() and os.access(path, os.W_OK) for path in (audit_dir, runtime_root)):
        raise SystemExit("Worker directories are not writable")
    print("CONTAINER_HEALTHY")


if __name__ == "__main__":
    main()
