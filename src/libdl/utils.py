from http import HTTPStatus


def http_status_to_msg(status: int) -> str:

    try:
        return str(status) + ' ' + HTTPStatus(status).phrase
    except ValueError:
        return str(status)
