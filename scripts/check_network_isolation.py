"""Prove real Chrome cannot bypass the job proxy for loopback traffic."""

import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from aveli.isolation import ChromeConfig, IsolatedChrome


class ProbeHandler(BaseHTTPRequestHandler):
    hits = 0

    def do_GET(self):
        type(self).hits += 1
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"unsafe")

    def log_message(self, _format, *_args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProbeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    denied = []
    config = ChromeConfig.from_env(os.environ)
    try:
        with IsolatedChrome(
            "loopback-check",
            config,
            allowed_hosts=frozenset({"allowed.example"}),
            on_network_denied=denied.append,
        ):
            from browser_harness.admin import ensure_daemon
            from browser_harness.helpers import cdp

            ensure_daemon()
            target = cdp(
                "Target.createTarget",
                url=f"http://127.0.0.1:{server.server_port}/must-be-blocked",
                background=True,
            )["targetId"]
            time.sleep(0.5)
            cdp("Target.closeTarget", targetId=target)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    assert ProbeHandler.hits == 0, "Chrome bypassed the host proxy and contacted loopback"
    assert "127.0.0.1" in denied
    print("LOOPBACK_BLOCK_PASS")


if __name__ == "__main__":
    main()
