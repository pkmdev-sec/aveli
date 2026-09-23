import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from aveli.moli import IsolatedMoli, MoliConfig


class FakeProcess:
    def __init__(self, returncode=None):
        self.returncode = returncode
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

def fake_moli(path, version="moli 1.1.9"):
    path.write_text(f"#!/bin/sh\necho '{version}'\n")
    path.chmod(0o755)
    return path


def fake_terminate(process):
    process.terminate()


def test_config_requires_an_existing_moli_binary(monkeypatch):
    monkeypatch.setenv("AVELI_MOLI_PATH", "/does/not/exist")
    with pytest.raises(ValueError, match="Moli executable"):
        MoliConfig.from_env(os.environ)

def test_config_requires_pinned_moli_version(tmp_path):
    executable = fake_moli(tmp_path / "moli", "moli 1.2.0")
    with pytest.raises(ValueError, match="1.1.9 is required; found moli 1.2.0"):
        MoliConfig.from_env({"AVELI_MOLI_PATH": str(executable)})


def test_config_accepts_exact_pinned_moli_version(tmp_path):
    executable = fake_moli(tmp_path / "moli")
    assert MoliConfig.from_env({"AVELI_MOLI_PATH": str(executable)}).executable == executable


def test_isolated_moli_uses_real_layout_and_restores_environment(tmp_path, monkeypatch):
    process = FakeProcess()
    launch = Mock(return_value=process)
    monkeypatch.setattr("aveli.moli.subprocess.Popen", launch)
    monkeypatch.setattr(IsolatedMoli, "_reserve_port", Mock(return_value=43124))
    monkeypatch.setattr(IsolatedMoli, "_ready", Mock(return_value=True))
    monkeypatch.setenv("BU_NAME", "original")
    stopped = Mock()
    config = MoliConfig(executable=Path("/fake/moli"), root=tmp_path, resource=True)

    with IsolatedMoli("checks", config, stop_daemon=stopped, terminate_process=fake_terminate) as runtime:
        args = launch.call_args.args[0]
        assert args == [
            "/fake/moli",
            "serve",
            "--host",
            "127.0.0.1",
            "--port",
            "43124",
            "--layout",
            "--profile-dir",
            str(runtime.profile_dir),
            "--resource",
        ]
        assert os.environ["BU_CDP_URL"] == "http://127.0.0.1:43124"
        assert os.environ["BU_NAME"] == runtime.daemon_name
        assert os.environ["BH_TAB_MARKER"] == "0"
        base_dir = runtime.base_dir

    assert stopped.call_args.args == (runtime.daemon_name,)
    assert process.terminated
    assert os.environ["BU_NAME"] == "original"
    assert not base_dir.exists()


def test_startup_timeout_is_bounded_without_process_output(tmp_path, monkeypatch):
    process = FakeProcess()
    monkeypatch.setattr("aveli.moli.subprocess.Popen", Mock(return_value=process))
    monkeypatch.setattr(IsolatedMoli, "_reserve_port", Mock(return_value=43125))
    monkeypatch.setattr(IsolatedMoli, "_ready", Mock(return_value=False))
    monotonic = Mock(side_effect=[0.0, 0.0, 0.2])
    monkeypatch.setattr("aveli.moli.time.monotonic", monotonic)
    monkeypatch.setattr("aveli.moli.time.sleep", Mock())
    config = MoliConfig(executable=Path("/fake/moli"), root=tmp_path, startup_timeout=0.1)

    with pytest.raises(TimeoutError, match="DevTools endpoint"):
        with IsolatedMoli("timeout", config, stop_daemon=Mock(), terminate_process=fake_terminate):
            pass

    assert process.terminated
