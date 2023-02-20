import os
import shutil
import uuid
from tempfile import gettempdir
from typing import BinaryIO, Optional, Tuple, cast
from urllib.parse import (
    quote,
    unquote,
    urlparse,
    uses_netloc,
    uses_params,
    uses_relative,
)
from urllib.request import Request, urlopen

from .util import FileLikeObj

_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
_VALID_URLS.discard("")
MAX_FILE_SIZE = 200


def localize_file(
    path_or_buffer: FileLikeObj,
    user_agent: Optional[str] = None,
    suffix: str = ".pdf",
    use_raw_url=False,
) -> Tuple[str, bool]:
    """Ensure localize target file.

    If the target file is remote, this function fetches into local storage.

    Args:
        path_or_buffer (str):
            File path or file like object or URL of target file.
        user_agent (str, optional):
            Set a custom user-agent when download a pdf from a url. Otherwise
            it uses the default ``urllib.request`` user-agent.
        suffix (str, optional):
            File extension to check.
        use_raw_url (bool):
            Use `path_or_buffer` without quoting/dequoting.

    Returns:
        (str, bool):
            tuple of str and bool, which represents file name in local storage
            and temporary file flag.
    """

    path_or_buffer = _stringify_path(path_or_buffer)
    safe_with_percent = "!#$%&'()*+,/:;=?@[]~"

    if _is_url(path_or_buffer):
        if not use_raw_url:
            path_or_buffer = quote(unquote(path_or_buffer), safe=safe_with_percent)
        if user_agent:
            req = urlopen(_create_request(path_or_buffer, user_agent))
        else:
            req = urlopen(path_or_buffer)

        parsed_url = urlparse(req.geturl())
        filename = os.path.basename(parsed_url.path)
        fname, ext = os.path.splitext(filename)
        filename = f"{fname[:MAX_FILE_SIZE]}{ext}"
        if ext != suffix:
            filename = f"{uuid.uuid4()}{suffix}"

        filename = os.path.join(gettempdir(), filename)
        with open(filename, "wb") as f:
            shutil.copyfileobj(req, f)

        return filename, True

    elif is_file_like(path_or_buffer):
        filename = os.path.join(gettempdir(), f"{uuid.uuid4()}{suffix}")
        path_or_buffer = cast(BinaryIO, path_or_buffer)
        path_or_buffer.seek(0)

        with open(filename, "wb") as f:
            shutil.copyfileobj(path_or_buffer, f)

        return filename, True

    # File path case
    else:
        return os.path.expanduser(path_or_buffer), False


def _is_url(url: str) -> bool:
    try:
        return urlparse(url).scheme in _VALID_URLS

    except Exception:
        return False


def _create_request(path_or_buffer: str, user_agent: str) -> Request:
    req_headers = {"User-Agent": user_agent}
    return Request(path_or_buffer, headers=req_headers)


def is_file_like(obj: FileLikeObj) -> bool:
    """Check file like object

    Args:
        obj:
            file like object.

    Returns:
        bool: file like object or not
    """

    if not (hasattr(obj, "read") or hasattr(obj, "write")):
        return False

    if not hasattr(obj, "__iter__"):
        return False

    return True


def _stringify_path(path_or_buffer: FileLikeObj) -> str:
    """Convert path like object to string

    Args:
        path_or_buffer: object to be converted

    Returns:
        string_path_or_buffer: maybe string version of path_or_buffer
    """

    try:
        import pathlib

        _PATHLIB_INSTALLED = True
    except ImportError:
        _PATHLIB_INSTALLED = False

    if hasattr(path_or_buffer, "__fspath__"):
        path_or_buffer = cast(os.PathLike, path_or_buffer)
        return path_or_buffer.__fspath__()

    if _PATHLIB_INSTALLED and isinstance(path_or_buffer, pathlib.Path):
        return str(path_or_buffer)

    path_or_buffer = cast(str, path_or_buffer)
    return path_or_buffer
