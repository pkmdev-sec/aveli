"""Explicit, experimental Moli runtime for Aveli compatibility checks."""

import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from .isolation import _terminate_process_group

_ENV_KEYS = (
    "BU_CDP_URL",
    "BU_CDP_WS",
    "BU_NAME",
    "BH_RUNTIME_DIR",
    "BH_TMP_DIR",
    "BH_RUNTIME_DIR_SHARED",
    "BH_TMP_DIR_SHARED",
    "BH_TAB_MARKER",
)


@dataclass(frozen=True)
class MoliConfig:
    executable: Path
    root: Path | None = None
    startup_timeout: float = 20.0
    resource: bool = False
    REQUIRED_VERSION = "moli 1.1.9"

    @classmethod
    def from_env(cls, environment: Mapping[str, str]) -> "MoliConfig":
        explicit = environment.get("AVELI_MOLI_PATH", "").strip()
        executable = Path(explicit).expanduser() if explicit else None
        if executable is None:
            found = shutil.which("moli")
            executable = Path(found) if found else None
        if executable is None or not executable.is_file():
            raise ValueError("Moli executable not found; set AVELI_MOLI_PATH to a Moli binary")
        try:
            version = subprocess.run(
                [str(executable), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError) as error:
            raise ValueError("Moli executable could not be validated") from error
        if version != cls.REQUIRED_VERSION:
            required = cls.REQUIRED_VERSION.removeprefix("moli ")
            raise ValueError(f"Moli {required} is required; found {version or 'unknown'}")
        root_value = environment.get("AVELI_RUNTIME_ROOT", "").strip()
        root = Path(root_value).expanduser() if root_value else None
        if root and not root.is_absolute():
            raise ValueError("AVELI_RUNTIME_ROOT must be an absolute path")
        return cls(executable=executable, root=root, resource=environment.get("AVELI_MOLI_RESOURCE") == "1")


class IsolatedMoli:
    """Own one loopback Moli server and Browser Harness namespace."""

    def __init__(
        self,
        name: str,
        config: MoliConfig,
        *,
        stop_daemon: Callable[[str], None] | None = None,
        terminate_process: Callable[[object], None] = _terminate_process_group,
    ):
        self.name = name
        self.config = config
        self._stop_daemon_override = stop_daemon
        self._terminate_process = terminate_process
        self._old_environment: dict[str, str | None] = {}
        self._stderr = None
        self.process = None
        self.base_dir = None
        self.runtime_dir = None
        self.tmp_dir = None
        self.profile_dir = None
        self.daemon_name = None

    def __enter__(self) -> "IsolatedMoli":
        if self.config.root:
            self.config.root.mkdir(parents=True, exist_ok=True)
        self.base_dir = Path(tempfile.mkdtemp(prefix="aveli-moli-", dir=self.config.root))
        self.runtime_dir = self.base_dir / "harness-runtime"
        self.tmp_dir = self.base_dir / "harness-tmp"
        self.profile_dir = self.base_dir / "profile"
        for path in (self.runtime_dir, self.tmp_dir, self.profile_dir):
            path.mkdir(mode=0o700)
        self.daemon_name = f"aveli-moli-{self.name}-{self.base_dir.name[-6:]}"
        self._stderr = (self.base_dir / "moli.log").open("wb")
        port = self._reserve_port()
        args = [
            str(self.config.executable),
            "serve",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--layout",
            "--profile-dir",
            str(self.profile_dir),
        ]
        if self.config.resource:
            args.append("--resource")
        try:
            self.process = subprocess.Popen(
                args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=self._stderr,
                start_new_session=True,
            )
            self._wait_until_ready(port)
            self._set_environment(port)
            return self
        except Exception:
            self.close(raise_errors=False)
            raise

    @staticmethod
    def _reserve_port() -> int:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            return listener.getsockname()[1]

    def _wait_until_ready(self, port: int) -> None:
        deadline = time.monotonic() + self.config.startup_timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"Moli exited during startup with code {self.process.returncode}")
            if self._ready(port):
                return
            time.sleep(0.05)
        raise TimeoutError("Moli did not publish a DevTools endpoint")

    @staticmethod
    def _ready(port: int) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=0.5) as response:
                data = json.load(response)
            return data.get("webSocketDebuggerUrl") == f"ws://127.0.0.1:{port}/devtools/browser/moli-browser"
        except (OSError, ValueError, json.JSONDecodeError):
            return False

    def _set_environment(self, port: int) -> None:
        self._old_environment = {key: os.environ.get(key) for key in _ENV_KEYS}
        for key in _ENV_KEYS:
            os.environ.pop(key, None)
        os.environ.update(
            {
                "BU_CDP_URL": f"http://127.0.0.1:{port}",
                "BU_NAME": self.daemon_name,
                "BH_RUNTIME_DIR": str(self.runtime_dir),
                "BH_TMP_DIR": str(self.tmp_dir),
                "BH_TAB_MARKER": "0",
            }
        )

    def _stop_daemon(self) -> None:
        if not self.daemon_name:
            return
        if self._stop_daemon_override:
            self._stop_daemon_override(self.daemon_name)
            return
        import sys

        if "browser_harness.admin" not in sys.modules:
            return
        from browser_harness.admin import restart_daemon

        restart_daemon(self.daemon_name, require_clean=True)

    def close(self, *, raise_errors: bool = True) -> None:
        errors = []
        try:
            self._stop_daemon()
        except Exception as error:
            errors.append(f"daemon cleanup: {type(error).__name__}")
        try:
            if self.process:
                self._terminate_process(self.process)
        except Exception as error:
            errors.append(f"Moli cleanup: {type(error).__name__}")
        self.process = None
        if self._stderr:
            self._stderr.close()
            self._stderr = None
        for key, value in self._old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self._old_environment.clear()
        if self.base_dir:
            shutil.rmtree(self.base_dir, ignore_errors=True)
            if self.base_dir.exists():
                errors.append("runtime directory cleanup failed")
        if errors and raise_errors:
            raise RuntimeError("; ".join(errors))

    def __exit__(self, *_args) -> None:
        self.close()
