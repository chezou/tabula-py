from pkg_resources import DistributionNotFound, get_distribution

from .util import environment_info
from .wrapper import (
    convert_into,
    convert_into_by_batch,
    read_pdf,
    read_pdf_with_template,
)

try:
    __version__ = get_distribution("tabula-py").version
except DistributionNotFound:
    # package is not installed
    pass
