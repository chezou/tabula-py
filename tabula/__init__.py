from importlib.metadata import PackageNotFoundError, version

from .io import convert_into, convert_into_by_batch, read_pdf, read_pdf_with_template
from .util import environment_info

try:
    __version__ = version("tabula-py")
except PackageNotFoundError:
    # package is not installed
    pass
