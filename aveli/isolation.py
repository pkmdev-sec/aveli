"""Ephemeral Chrome and Browser Harness runtime for one production job process."""

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .network import AllowedHostProxy

_ACTIVE_ISOLATION = None


def require_active_isolation() -> "IsolatedChrome":
    if _ACTIVE_ISOLATION is None:
        raise RuntimeError("ProductionRunner requires an active IsolatedChrome context")
    return _ACTIVE_ISOLATION


@dataclass(frozen=True)
class ChromeConfig:
    executable: Path
    root: Path | None = None
    startup_timeout: float = 20.0
    headless: bool = True

    @classmethod
    def from_env(cls, environment: Mapping[str, str]) -> "ChromeConfig":
        explicit = environment.get("AVELI_CHROME_PATH", "").strip()
        candidates = [Path(explicit)] if explicit else _chrome_candidates()
        executable = next((path for path in candidates if path.is_file()), None)
        if executable is None:
            raise ValueError("Chrome executable not found; set AVELI_CHROME_PATH to a dedicated Chromium binary")
        root_value = environment.get("AVELI_RUNTIME_ROOT", "").strip()
        root = Path(root_value).expanduser() if root_value else None
        if root and not root.is_absolute():
            raise ValueError("AVELI_RUNTIME_ROOT must be an absolute path")
        return cls(executable=executable, root=root)


def _chrome_candidates() -> list[Path]:
    names = ["google-chrome-stable", "google-chrome", "chromium", "chromium-browser"]
    paths = [Path(found) for name in names if (found := shutil.which(name))]
    if sys.platform == "darwin":
        paths.extend(
            [
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                Path("/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
                Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
            ]
        )
    return paths


def _terminate_process_group(process) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
        else:
            process.kill()
        process.wait(timeout=5)
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


class IsolatedChrome:
    """Own one Chrome process, profile, CDP endpoint, and harness daemon namespace."""

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

    def __init__(
        self,
        job_id: str,
        config: ChromeConfig,
        *,
        stop_daemon: Callable[[str], None] | None = None,
        allowed_hosts: frozenset[str] | None = None,
        on_network_denied: Callable[[str], None] | None = None,
        on_cleanup_failure: Callable[[str], None] | None = None,
        terminate_process: Callable[[object], None] = _terminate_process_group,
    ):
        self.job_id = job_id
        self.config = config
        self._stop_daemon_override = stop_daemon
        self.allowed_hosts = allowed_hosts
        self.on_network_denied = on_network_denied
        self.on_cleanup_failure = on_cleanup_failure
        self._terminate_process = terminate_process
        self._proxy = None
        self._old_environment: dict[str, str | None] = {}
        self._stderr = None
        self.process = None
        self.base_dir = None
        self.profile_dir = None
        self.runtime_dir = None
        self.tmp_dir = None
        self.daemon_name = None

    def __enter__(self) -> "IsolatedChrome":
        global _ACTIVE_ISOLATION
        if _ACTIVE_ISOLATION is not None:
            raise RuntimeError("Only one isolated Chrome job may run in a process")
        if self._stop_daemon_override is None and any(
            name == "browser_harness" or name.startswith("browser_harness.") for name in sys.modules
        ):
            raise RuntimeError("Enter IsolatedChrome before importing Agent or browser_harness")
        if self.config.root:
            self.config.root.mkdir(parents=True, exist_ok=True)
        self.base_dir = Path(tempfile.mkdtemp(prefix="aveli-job-", dir=self.config.root))
        self.profile_dir = self.base_dir / "profile"
        self.runtime_dir = self.base_dir / "harness-runtime"
        self.tmp_dir = self.base_dir / "harness-tmp"
        for path in (self.profile_dir, self.runtime_dir, self.tmp_dir):
            path.mkdir(mode=0o700)
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "-", self.job_id)[:40] or "job"
        self.daemon_name = f"aveli-{safe_id}-{self.base_dir.name[-6:]}"
        self._stderr = (self.base_dir / "chrome.log").open("wb")
        if self.allowed_hosts is not None:
            self._proxy = AllowedHostProxy(self.allowed_hosts, self.on_network_denied)
            self._proxy.__enter__()
        args = [
            str(self.config.executable),
            "--remote-debugging-address=127.0.0.1",
            "--remote-debugging-port=0",
            f"--user-data-dir={self.profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-sync",
            "--metrics-recording-only",
            "--disable-quic",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
        ]
        if self._proxy:
            proxy_host, proxy_port = self._proxy.address
            args.append(f"--proxy-server=http://{proxy_host}:{proxy_port}")
            args.append("--proxy-bypass-list=<-loopback>")
        if self.config.headless:
            args.append("--headless=new")
        args.append("about:blank")
        try:
            self.process = subprocess.Popen(
                args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=self._stderr,
                start_new_session=True,
            )
            port = self._wait_for_port()
            self._set_environment(port)
            _ACTIVE_ISOLATION = self
            return self
        except Exception:
            self.close(raise_errors=False)
            raise

    def _wait_for_port(self) -> int:
        active_port = self.profile_dir / "DevToolsActivePort"
        deadline = time.monotonic() + self.config.startup_timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"Isolated Chrome exited during startup with code {self.process.returncode}")
            try:
                port = int(active_port.read_text(encoding="utf-8").splitlines()[0])
                if 0 < port < 65536:
                    return port
            except (FileNotFoundError, ValueError, IndexError):
                pass
            time.sleep(0.05)
        raise TimeoutError("Isolated Chrome did not publish a DevTools endpoint")

    def _set_environment(self, port: int) -> None:
        self._old_environment = {key: os.environ.get(key) for key in self._ENV_KEYS}
        for key in self._ENV_KEYS:
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
        if "browser_harness.admin" not in sys.modules:
            return
        from browser_harness.admin import restart_daemon

        restart_daemon(self.daemon_name, require_clean=True)

    def close(self, *, raise_errors: bool = True) -> None:
        global _ACTIVE_ISOLATION
        if _ACTIVE_ISOLATION is self:
            _ACTIVE_ISOLATION = None
        errors = []
        try:
            self._stop_daemon()
        except Exception as error:
            errors.append(f"daemon cleanup: {type(error).__name__}")
        try:
            if self.process:
                self._terminate_process(self.process)
        except Exception as error:
            errors.append(f"Chrome cleanup: {type(error).__name__}")
        self.process = None
        try:
            if self._proxy:
                self._proxy.close()
        except Exception as error:
            errors.append(f"proxy cleanup: {type(error).__name__}")
        self._proxy = None
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
        for error in errors:
            if self.on_cleanup_failure:
                self.on_cleanup_failure(error)
        if errors and raise_errors:
            raise RuntimeError("; ".join(errors))

    def __exit__(self, *_args) -> None:
        self.close()
