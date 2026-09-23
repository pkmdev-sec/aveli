import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from aveli.isolation import ChromeConfig, IsolatedChrome, _terminate_process_group


class FakeProcess:
    def __init__(self):
        self.pid = 4321
        self.returncode = None
        self.terminated = False
        self.killed = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None):
        if self.returncode is None:
            raise TimeoutError()
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


def fake_terminate(process):
    process.terminate()


def fake_popen(created):
    def launch(args, **kwargs):
        profile_arg = next(arg for arg in args if arg.startswith("--user-data-dir="))
        profile = Path(profile_arg.split("=", 1)[1])
        profile.mkdir(parents=True, exist_ok=True)
        (profile / "DevToolsActivePort").write_text("43123\n/devtools/browser/test\n")
        process = FakeProcess()
        created.append((process, args, kwargs))
        return process

    return launch


def test_isolation_sets_explicit_endpoint_and_unique_runtime_then_cleans(tmp_path, monkeypatch):
    created = []
    monkeypatch.setattr("aveli.isolation.subprocess.Popen", fake_popen(created))
    stopped = Mock()
    config = ChromeConfig(executable=Path("/fake/chrome"), root=tmp_path)

    with IsolatedChrome("job-one", config, stop_daemon=stopped, terminate_process=fake_terminate) as first:
        first_paths = (first.profile_dir, first.runtime_dir)
        assert os.environ["BU_CDP_URL"] == "http://127.0.0.1:43123"
        assert os.environ["BU_NAME"] == first.daemon_name
        assert os.environ["BH_RUNTIME_DIR"] == str(first.runtime_dir)
        assert first.profile_dir.exists()

    assert stopped.call_args.args == (first.daemon_name,)
    assert created[0][0].terminated
    assert not first_paths[0].exists()
    assert "BU_CDP_URL" not in os.environ

    with IsolatedChrome("job-two", config, stop_daemon=stopped, terminate_process=fake_terminate) as second:
        assert (second.profile_dir, second.runtime_dir) != first_paths


def test_isolation_cleans_up_when_job_fails(tmp_path, monkeypatch):
    created = []
    monkeypatch.setattr("aveli.isolation.subprocess.Popen", fake_popen(created))
    config = ChromeConfig(executable=Path("/fake/chrome"), root=tmp_path)
    isolated = IsolatedChrome("failed-job", config, stop_daemon=Mock(), terminate_process=fake_terminate)
    with pytest.raises(RuntimeError, match="job failed"):
        with isolated:
            raise RuntimeError("job failed")
    assert created[0][0].terminated
    assert not isolated.profile_dir.exists()


def test_chrome_config_requires_real_explicit_binary(monkeypatch):
    monkeypatch.setenv("AVELI_CHROME_PATH", "/does/not/exist")
    with pytest.raises(ValueError, match="Chrome executable"):
        ChromeConfig.from_env(os.environ)


def test_chrome_forces_loopback_through_allowlist_proxy(tmp_path, monkeypatch):
    created = []
    monkeypatch.setattr("aveli.isolation.subprocess.Popen", fake_popen(created))
    config = ChromeConfig(executable=Path("/fake/chrome"), root=tmp_path)
    with IsolatedChrome(
        "proxy-job",
        config,
        stop_daemon=Mock(),
        terminate_process=fake_terminate,
        allowed_hosts=frozenset({"allowed.example"}),
    ):
        args = created[0][1]
        assert "--proxy-bypass-list=<-loopback>" in args
        assert any(arg.startswith("--proxy-server=http://127.0.0.1:") for arg in args)


def test_process_group_is_terminated(monkeypatch):
    process = FakeProcess()
    calls = []

    def killpg(pid, sig):
        calls.append((pid, sig))
        process.returncode = 0

    monkeypatch.setattr("aveli.isolation.os.killpg", killpg)
    _terminate_process_group(process)
    assert calls[0][0] == process.pid
