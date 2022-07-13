import cgi
import os.path
import urllib
from typing import Optional

import urllib3

from libdl.exceptions import ClientError, Error, InvalidURL, ServerError
from libdl.utils import http_status_to_msg

DOWNLOAD_CHUNK_SIZE = 1024 * 64


class Download:
    """
    A class represents one download.

    :param engine:
        A :class:`libdl.DownloadEngine` instance.
    :param url:
        An HTTP(S) URL to download.
    :param dir:
        The directory where the downloaded file will be saved, defaults
        to the current directory.
    :param filename:
        The Name for the downloaded file, if not given the name will be
        extracted from ``Content-Disposation`` HTTP Header if it is not
        pressent it will fall back to URL otherwise the name is
        ``index.html``.
    """

    #: The directory where the downloaded file will be saved.
    dir: str

    #: The Name for the downloaded file.
    filename: str

    #: The absolute path of the downloaded file.
    path: str

    #: File size in bytes or ``None`` if unknown.
    filesize: Optional[int]

    def __init__(
        self,
        engine: "DownloadEngine",
        url: str,
        dir: str = '.',
        filename: Optional[str] = None,
    ) -> None:
        try:
            self._response = engine._pool.request('GET', url, preload_content=False)
        except urllib3.exceptions.LocationValueError:
            raise InvalidURL('Invalid URL: ' + url)
        except urllib3.exceptions.HTTPError:
            raise Error('Error: ' + url)

        if 400 <= self._response.status < 500:
            raise ClientError('Client Error: ' + http_status_to_msg(self._response.status))
        if 500 <= self._response.status < 600:
            raise ServerError('Server Error: ' + http_status_to_msg(self._response.status))

        if filename is None:
            filename = self._get_filename()
        self.filename = filename
        self.filesize = self._get_filesize()
        self.dir = os.path.abspath(dir)
        self.path = os.path.join(dir, filename)

    def run(self) -> None:
        """Start the download."""
        with open(self.path, 'wb') as f:
            for chunk in self._response.stream(DOWNLOAD_CHUNK_SIZE):
                f.write(chunk)
        self._response.release_conn()

    def _get_filesize(self) -> Optional[int]:
        try:
            return int(self._response.getheader('Content-Length'))
        except TypeError:
            return None

    def _get_filename(self) -> str:
        content_disposition = self._response.getheader('Content-Disposition')
        if content_disposition:
            path = cgi.parse_header(content_disposition)[1].get('filename')
        else:
            path = urllib3.util.parse_url(self._response.geturl()).path

        if path:
            filename = os.path.basename(path)
            if filename:
                return urllib.parse.unquote(filename)
        return 'index.html'


class DownloadEngine:

    def __init__(self) -> None:
        self._pool = urllib3.PoolManager()

    def create_download(
        self,
        url: str,
        dir: str = '.',
        filename: Optional[str] = None
    ) -> Download:
        """
        Create a new download and return a :class:`libdl.Download`
        instance. `url`, `dir` and `filename` are the same as in
        :class:`libdl.Download`
        """
        return Download(self, url, dir, filename)
