"""Structured, redacted operational audit events."""

import json
import os
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse


class AuditSink(Protocol):
    def emit(self, event: str, fields: Mapping[str, Any]) -> None: ...


class NullAuditSink:
    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        pass


class JsonlAuditSink:
    """Append one redacted event per line; one sink belongs to one job process."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()

    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        record = {
            "schema_version": 1,
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            **_redact(dict(fields)),
        }
        line = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._lock:
            flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(self.path, flags, 0o600)
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
                stream.write(line + "\n")


def _redact(value: Any, key: str = "") -> Any:
    lowered = key.lower()
    if lowered in {"value", "typed_value"} or any(
        part in lowered
        for part in ("secret", "password", "token", "api_key", "authorization", "cookie", "goal", "page_text")
    ):
        return "<redacted>"
    if isinstance(value, Mapping):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item, key) for item in value]
    if key.endswith("url") and isinstance(value, str):
        parsed = urlparse(value)
        return f"{parsed.scheme}://{parsed.hostname or ''}/<redacted>"
    if isinstance(value, str):
        value = re.sub(r"(?i)bearer\s+[^\s,;]+", "Bearer <redacted>", value)
        value = re.sub(r"(?i)(api[_-]?key|token|password|secret)=([^&\s]+)", r"\1=<redacted>", value)
        if len(value) > 256:
            return value[:253] + "..."
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
