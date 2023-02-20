"""
Utility module providing some convenient functions.
"""

from __future__ import annotations

import os
import platform
import shlex
from dataclasses import dataclass
from logging import getLogger
from typing import IO, Iterable, List, Optional, Union, cast

logger = getLogger(__name__)

FileLikeObj = Union[IO, str, os.PathLike]


def java_version() -> str:
    """Show Java version

    Returns:
        str: Result of ``java -version``
    """
    import subprocess

    try:
        res = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT
        ).decode()

    except FileNotFoundError:
        res = (
            "`java -version` faild. `java` command is not found from this Python"
            "process. Please ensure Java is installed and PATH is set for `java`"
        )

    return res


def environment_info() -> None:
    """Show environment information for reporting.

    Returns:
        str:
            Detailed information like Python version, Java version,
            or OS environment, etc.
    """

    import sys

    import distro

    from tabula import __version__

    print(
        f"""Python version:
    {sys.version}
Java version:
    {java_version().strip()}
tabula-py version: {__version__}
platform: {platform.platform()}
uname:
    {str(platform.uname())}
linux_distribution: ('{distro.name()}', '{distro.version()}', '{distro.codename()}')
mac_ver: {platform.mac_ver()}"""
    )


@dataclass
class TabulaOption:
    """Build options for tabula-java

    Args:
        pages (str, int, `iterable` of `int`, optional):
            An optional values specifying pages to extract from. It allows
            `str`,`int`, `iterable` of :`int`. Default: `1`

            Examples:
                ``'1-2,3'``, ``'all'``, ``[1,2]``
        guess (bool, optional):
            Guess the portion of the page to analyze per page. Default `True`
            If you use "area" option, this option becomes `False`.

            Note:
                As of tabula-java 1.0.3, guess option becomes independent from
                lattice and stream option, you can use guess and lattice/stream option
                at the same time.

        area (iterable of float, iterable of iterable of float, optional):
            Portion of the page to analyze(top,left,bottom,right).
            Default is entire page.

            Note:
                If you want to use multiple area options and extract in one table, it
                should be better to set ``multiple_tables=False`` for :func:`read_pdf()`

            Examples:
                ``[269.875,12.75,790.5,561]``,
                ``[[12.1,20.5,30.1,50.2], [1.0,3.2,10.5,40.2]]``

        relative_area (bool, optional):
            If all area values are between 0-100 (inclusive) and preceded by ``'%'``,
            input will be taken as % of actual height or width of the page.
            Default ``False``.
        lattice (bool, optional):
            Force PDF to be extracted using lattice-mode extraction
            (if there are ruling lines separating each cell, as in a PDF of an
            Excel spreadsheet)
        stream (bool, optional):
            Force PDF to be extracted using stream-mode extraction
            (if there are no ruling lines separating each cell, as in a PDF of an
            Excel spreadsheet)
        password (str, optional):
            Password to decrypt document. Default: empty
        silent (bool, optional):
            Suppress all stderr output.
        columns (iterable, optional):
            X coordinates of column boundaries.

            Example:
                ``[10.1, 20.2, 30.3]``
        relative_columns (bool, optional):
            If all values are between 0-100 (inclusive) and preceded by '%',
            input will be taken as % of actual width of the page.
            Default ``False``.
        format (str, optional):
            Format for output file or extracted object.
            (``"CSV"``, ``"TSV"``, ``"JSON"``)
        batch (str, optional):
            Convert all PDF files in the provided directory. This argument should be
            directory path.
        output_path (str, optional):
            Output file path. File format of it is depends on ``format``.
            Same as ``--outfile`` option of tabula-java.
        options (str, optional):
            Raw option string for tabula-java.
        multiple_tables (bool, optional):
            Extract multiple tables into a dataframe. Default: True
    """

    pages: Optional[Union[str, int, Iterable[int]]] = None
    guess: bool = True
    area: Optional[Union[Iterable[float], Iterable[Iterable[float]]]] = None
    relative_area: bool = False
    lattice: bool = False
    stream: bool = False
    password: Optional[str] = None
    silent: Optional[bool] = None
    columns: Optional[Iterable[float]] = None
    relative_columns: bool = False
    format: Optional[str] = None
    batch: Optional[str] = None
    output_path: Optional[str] = None
    options: Optional[str] = ""
    multiple_tables: bool = True

    def merge(self, other: TabulaOption) -> TabulaOption:
        """Merge two TabulaOption.
        self will overwrite other fields' values.
        """
        return TabulaOption(
            pages=self.pages or other.pages,
            guess=self.guess or other.guess,
            area=self.area or other.area,
            relative_area=self.relative_area or other.relative_area,
            lattice=self.lattice or other.lattice,
            stream=self.stream or other.stream,
            password=self.password or other.password,
            silent=self.silent or other.silent,
            columns=self.columns or other.columns,
            relative_columns=self.relative_columns or other.relative_columns,
            format=self.format or other.format,
            batch=self.batch or other.batch,
            output_path=self.output_path or other.output_path,
            options=self.options or other.options,
            multiple_tables=self.multiple_tables or other.multiple_tables,
        )

    def build_option_list(self) -> List[str]:
        """Convert to tabula-java option list"""
        __options = []
        # handle options described in string for backward compatibility
        if self.options:
            __options += shlex.split(self.options)

        if self.pages:
            __pages = self.pages
            if isinstance(self.pages, int):
                __pages = str(self.pages)
            elif type(self.pages) in [list, tuple]:
                __pages = ",".join(map(str, self.pages))

            __pages = cast(str, __pages)
            __options += ["--pages", __pages]
        else:
            logger.warning(
                "'pages' argument isn't specified."
                "Will extract only from page 1 by default."
            )

        multiple_areas = False

        if self.area:
            self.guess = False
            if type(self.area) in [list, tuple]:
                # Check if nested list or tuple for multiple areas
                if any(type(e) in [list, tuple] for e in self.area):
                    for e in self.area:
                        e = cast(Iterable[float], e)
                        _validate_area(e)
                        __area = _format_with_relative(e, self.relative_area)
                        __options += ["--area", __area]
                        multiple_areas = True

                else:
                    area = cast(Iterable[float], self.area)
                    _validate_area(area)
                    __area = _format_with_relative(area, self.relative_area)
                    __options += ["--area", __area]

        if self.lattice:
            __options.append("--lattice")

        if self.stream:
            __options.append("--stream")

        if self.guess and not multiple_areas:
            __options.append("--guess")

        if self.format:
            __options += ["--format", self.format]

        if self.output_path:
            __options += ["--outfile", self.output_path]

        if self.columns:
            if self.columns != sorted(self.columns):
                raise ValueError("columns option should be sorted")

            __columns = _format_with_relative(self.columns, self.relative_columns)
            __options += ["--columns", __columns]

        if self.password:
            __options += ["--password", self.password]

        if self.batch:
            __options += ["--batch", self.batch]

        if self.silent:
            __options.append("--silent")

        return __options


def _format_with_relative(values: Iterable[float], is_relative: bool) -> str:
    percent = "%" if is_relative else ""
    value_str = ",".join(map(str, values))

    return f"{percent}{value_str}"


def _validate_area(values: Iterable[float]) -> None:
    value_length = len(list(values))
    if value_length != 4:
        raise ValueError(
            f"area should have 4 values for each option but {values} has {value_length}"
        )
    top, left, bottom, right = values
    if top >= bottom:
        raise ValueError(
            f"area option bottom={bottom} should be greater than top={top}"
        )
    if left >= right:
        raise ValueError(
            f"area option right={right} should be greater than left={left}"
        )
