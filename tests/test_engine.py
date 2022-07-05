import io
from pathlib import Path
from typing import Callable, Dict, Optional

import pytest
from urllib3.exceptions import HTTPError, LocationValueError
from urllib3.response import HTTPResponse

import libdl
from libdl.exceptions import ClientError, Error, InvalidURL, ServerError


def mock_request(
    body: bytes = b'',
    status: int = 0,
    response_headers: Optional[Dict[str, str]] = None,
    exce: Optional[Exception] = None,
) -> Callable[[str, str, bool], HTTPResponse]:

    def request(method: str, url: str, preload_content: bool = True) -> HTTPResponse:

        nonlocal body
        fp = io.BytesIO(body)
        if exce is not None:
            raise exce
        return HTTPResponse(
            request_method=method,
            request_url=url,
            preload_content=preload_content,
            body=fp,
            status=status,
            headers=response_headers,
        )

    return request


class TestDownload:

    def test_with_400_status(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request(status=400))
        with pytest.raises(ClientError) as exce:
            dlengine.create_download('https://www.example.com/')
        assert str(exce.value) == 'Client Error: 400 Bad Request'

    def test_with_500_status(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request(status=500))
        with pytest.raises(ServerError) as exce:
            dlengine.create_download('https://www.example.com/')
        assert str(exce.value) == 'Server Error: 500 Internal Server Error'

    def test_with_filename_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request())

        download = dlengine.create_download('https://www.example.com')
        assert download.filename == 'index.html'

        download = dlengine.create_download('https://www.example.com/file.zip')
        assert download.filename == 'file.zip'

        download = dlengine.create_download('https://www.example.com/file%20with%20spaces.zip')
        assert download.filename == 'file with spaces.zip'

        monkeypatch.setattr(
            dlengine._pool,
            'request',
            mock_request(
                response_headers={'Content-Disposition': 'attachment; filename=file.zip'}
            ),
        )
        download = dlengine.create_download('https://www.example.com/')
        assert download.filename == 'file.zip'

        monkeypatch.setattr(
            dlengine._pool,
            'request',
            mock_request(
                response_headers={
                    'Content-Disposition': 'attachment; filename=file%20with%20spaces.zip'
                },
            ),
        )
        download = dlengine.create_download('https://www.example.com/')
        assert download.filename == 'file with spaces.zip'

    def test_with_filename(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request())
        download = dlengine.create_download('https://www.example.com/', filename='file.zip')
        assert download.filename == 'file.zip'

    def test_get_filesize(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request())
        download = dlengine.create_download('https://www.example.com/')
        assert download.filesize is None

        monkeypatch.setattr(
            dlengine._pool, 'request', mock_request(response_headers={'Content-Length': '125'})
        )
        download = dlengine.create_download('https://www.example.com/')
        assert download.filesize == 125

    def test_with_exceptions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request(exce=LocationValueError()))
        with pytest.raises(InvalidURL) as exce:
            dlengine.create_download('https://@"@@/')
        assert str(exce.value) == 'Invalid URL: https://@"@@/'

        monkeypatch.setattr(dlengine._pool, 'request', mock_request(exce=HTTPError()))
        with pytest.raises(Error) as exce:  # type: ignore[assignment]
            dlengine.create_download('https://www.example.com/')
        assert str(exce.value) == 'Error: https://www.example.com/'

    def test_run(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        dlengine = libdl.DownloadEngine()
        monkeypatch.setattr(dlengine._pool, 'request', mock_request(body=b'abcdef'))
        download = dlengine.create_download(
            'https://www.example.com/', str(tmp_path), 'file.txt'
        )
        assert download.dir == str(tmp_path)
        assert download.filename == 'file.txt'
        assert download.path == str(tmp_path / 'file.txt')
        assert download.filesize is None
        download.run()
        assert (tmp_path / 'file.txt').exists()
        assert (tmp_path / 'file.txt').stat().st_size == 6
