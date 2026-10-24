"""Skip HTTP transport checks only when the host explicitly denies loopback."""

import errno
import socket

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "http: requires the Windows loopback transport")


def pytest_collection_modifyitems(items):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        try:
            with socket.create_connection(listener.getsockname(), timeout=1):
                pass
        except OSError as error:
            if error.errno not in (errno.EACCES, errno.EPERM):
                raise
            skip = pytest.mark.skip(reason="Host denies loopback (EACCES); HTTP transport not verified.")
            for item in items:
                if item.get_closest_marker("http"):
                    item.add_marker(skip)
