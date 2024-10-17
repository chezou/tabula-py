from importlib.metadata import PackageNotFoundError, version

from .io import convert_into, convert_into_by_batch, read_pdf, read_pdf_with_template  # noqa: F401
from .util import environment_info  # noqa: F401

try:
    __version__ = version("tabula-py")
except PackageNotFoundError:
    # package is not installed
    pass
