import socket

from aveli.network import AllowedHostProxy


def request(proxy, payload):
    with socket.create_connection(proxy.address, timeout=2) as client:
        client.sendall(payload)
        return client.recv(1024)


def test_proxy_denies_undeclared_connect_without_contacting_destination():
    denied = []
    with AllowedHostProxy({"allowed.example"}, denied.append) as proxy:
        response = request(proxy, b"CONNECT denied.example:443 HTTP/1.1\r\nHost: denied.example\r\n\r\n")
    assert b"403" in response
    assert denied == ["denied.example"]


def test_proxy_denies_plain_http_and_non_tls_ports():
    denied = []
    with AllowedHostProxy({"allowed.example"}, denied.append) as proxy:
        plain = request(proxy, b"GET http://allowed.example/ HTTP/1.1\r\nHost: allowed.example\r\n\r\n")
        wrong_port = request(proxy, b"CONNECT allowed.example:8443 HTTP/1.1\r\nHost: allowed.example\r\n\r\n")
    assert b"403" in plain and b"403" in wrong_port
    assert denied == ["allowed.example", "allowed.example"]
