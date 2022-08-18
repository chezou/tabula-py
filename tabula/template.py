import json
from typing import Dict, Iterable, List, TextIO, Union, cast

from .file_util import _stringify_path, is_file_like
from .util import FileLikeObj, TabulaOption


def load_template(path_or_buffer: FileLikeObj) -> List[TabulaOption]:
    """Build tabula-py option from template file

    Args:
        path_or_buffer (str, path object or file-like object):
            File like object of Tabula app template.

    Returns:
        dict: tabula-py options
    """

    from itertools import groupby
    from operator import itemgetter

    path_or_buffer = _stringify_path(path_or_buffer)

    if is_file_like(path_or_buffer):
        path_or_buffer = cast(TextIO, path_or_buffer)
        templates = json.load(path_or_buffer)
    else:
        with open(path_or_buffer, "r") as f:
            templates = json.load(f)

    options = []

    grouper = itemgetter("page", "extraction_method")

    for key, grp in groupby(sorted(templates, key=grouper), grouper):
        tmp_options = [_convert_template_option(e) for e in grp]

        if len(tmp_options) == 1:
            options.append(tmp_options[0])
            continue

        option = tmp_options[0]
        _areas = [cast(Iterable[float], e.area) for e in tmp_options]
        option.area = _areas
        option.multiple_tables = True
        options.append(option)

    return options


def _convert_template_option(
    template: Dict[str, Union[bool, float, int, str]]
) -> TabulaOption:
    """Convert Tabula app template to tabula-py option

    Args:
        template (dict): Tabula app template

    Returns:
        `obj`:dict: tabula-py option
    """

    extraction_method = template.get("extraction_method")
    guess = False
    lattice = False
    stream = False
    if extraction_method == "guess":
        guess = True
    elif extraction_method == "lattice":
        lattice = True
    elif extraction_method == "stream":
        stream = True

    pages = cast(int, template.get("page"))
    area = [
        round(cast(float, template["y1"]), 3),
        round(cast(float, template["x1"]), 3),
        round(cast(float, template["y2"]), 3),
        round(cast(float, template["x2"]), 3),
    ]
    option = TabulaOption(
        guess=guess, lattice=lattice, stream=stream, pages=pages, area=area
    )

    return option
