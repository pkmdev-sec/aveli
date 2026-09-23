"""Small fail-closed CONNECT proxy for a job's declared browser hosts."""

import select
import socket
import threading
from collections.abc import Callable, Iterable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class _ProxyServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, allowed_hosts: frozenset[str], on_denied: Callable[[str], None]):
        self.allowed_hosts = allowed_hosts
        self.on_denied = on_denied
        super().__init__(("127.0.0.1", 0), _ProxyHandler)


class _ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_CONNECT(self) -> None:
        destination = urlsplit("//" + self.path)
        host = (destination.hostname or "").rstrip(".").lower()
        try:
            port = destination.port
        except ValueError:
            port = None
        if host not in self.server.allowed_hosts or port != 443:
            self.server.on_denied(host or "<invalid>")
            self.send_error(403, "Browser destination is not allowed")
            return
        try:
            upstream = socket.create_connection((host, port), timeout=10)
        except OSError:
            self.send_error(502, "Browser destination is unavailable")
            return
        self.send_response(200, "Connection established")
        self.end_headers()
        self.connection.settimeout(30)
        upstream.settimeout(30)
        try:
            peers = (self.connection, upstream)
            while True:
                readable, _, _ = select.select(peers, (), (), 30)
                if not readable:
                    break
                for source in readable:
                    data = source.recv(65536)
                    if not data:
                        return
                    destination_socket = upstream if source is self.connection else self.connection
                    destination_socket.sendall(data)
        except OSError:
            pass
        finally:
            upstream.close()

    def _deny_http(self) -> None:
        host = (urlsplit(self.path).hostname or self.headers.get("Host", "").split(":", 1)[0]).rstrip(".").lower()
        self.server.on_denied(host or "<invalid>")
        self.send_error(403, "Plain HTTP browser requests are not allowed through the proxy")

    do_GET = _deny_http
    do_POST = _deny_http
    do_PUT = _deny_http
    do_PATCH = _deny_http
    do_DELETE = _deny_http
    do_OPTIONS = _deny_http
    do_HEAD = _deny_http

    def log_message(self, _format, *_args) -> None:
        pass


class AllowedHostProxy:
    def __init__(self, allowed_hosts: Iterable[str], on_denied: Callable[[str], None] | None = None):
        self._server = _ProxyServer(
            frozenset(host.rstrip(".").lower() for host in allowed_hosts), on_denied or (lambda _: None)
        )
        self._thread = threading.Thread(target=self._server.serve_forever, name="aveli-host-proxy", daemon=True)

    @property
    def address(self) -> tuple[str, int]:
        host, port = self._server.server_address
        return str(host), int(port)

    def __enter__(self) -> "AllowedHostProxy":
        self._thread.start()
        return self

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        if self._thread.is_alive():
            self._thread.join(timeout=2)

    def __exit__(self, *_args) -> None:
        self.close()
