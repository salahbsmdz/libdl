from libdl.utils import http_status_to_msg


def test_http_status_to_msg() -> None:
    assert http_status_to_msg(404) == '404 Not Found'
    assert http_status_to_msg(599) == '599'
