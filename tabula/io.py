"""This module is a wrapper of tabula, which enables table extraction from a PDF.

This module extracts tables from a PDF into a pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Instead of importing this module, you can import public interfaces such as
:func:`read_pdf()`, :func:`read_pdf_with_template()`, :func:`convert_into()`,
:func:`convert_into_by_batch()` from `tabula` module directory.

Note:
    If you want to use your own tabula-java JAR file, set ``TABULA_JAR`` to
    environment variable for JAR path.

Example:

    >>> import tabula
    >>> df = tabula.read_pdf("/path/to/sample.pdf", pages="all")
"""

import errno
import io
import json
import os
import platform
import shlex
import subprocess
from collections import defaultdict
from logging import getLogger

import numpy as np
import pandas as pd

from .errors import CSVParseError, JavaNotFoundError
from .file_util import localize_file
from .template import load_template

logger = getLogger(__name__)

TABULA_JAVA_VERSION = "1.0.5"
JAR_NAME = "tabula-{}-jar-with-dependencies.jar".format(TABULA_JAVA_VERSION)
JAR_DIR = os.path.abspath(os.path.dirname(__file__))
JAVA_NOT_FOUND_ERROR = (
    "`java` command is not found from this Python process."
    "Please ensure Java is installed and PATH is set for `java`"
)

DEFAULT_CONFIG = {"JAR_PATH": os.path.join(JAR_DIR, JAR_NAME)}


def _jar_path():
    return os.environ.get("TABULA_JAR", DEFAULT_CONFIG["JAR_PATH"])


def _run(java_options, options, path=None, encoding="utf-8"):
    """Call tabula-java with the given lists of Java options and tabula-py
    options, as well as an optional path to pass to tabula-java as a regular
    argument and an optional encoding to use for any required output sent to
    stderr.

    tabula-py options are translated into tabula-java options, see
    :func:`build_options` for more information.
    """
    # Workaround to enforce the silent option. See:
    # https://github.com/tabulapdf/tabula-java/issues/231#issuecomment-397281157
    if options.get("silent"):
        java_options.extend(
            (
                "-Dorg.slf4j.simpleLogger.defaultLogLevel=off",
                "-Dorg.apache.commons.logging.Log"
                "=org.apache.commons.logging.impl.NoOpLog",
            )
        )

    built_options = build_options(**options)
    args = ["java"] + java_options + ["-jar", _jar_path()] + built_options
    if path:
        args.append(path)

    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            check=True,
        )
        if result.stderr:
            logger.warning("Got stderr: {}".format(result.stderr.decode(encoding)))
        return result.stdout
    except FileNotFoundError:
        raise JavaNotFoundError(JAVA_NOT_FOUND_ERROR)
    except subprocess.CalledProcessError as e:
        logger.error("Error from tabula-java:\n{}\n".format(e.stderr.decode(encoding)))
        raise


def read_pdf(
    input_path,
    output_format=None,
    encoding="utf-8",
    java_options=None,
    pandas_options=None,
    multiple_tables=True,
    user_agent=None,
    **kwargs
):
    """Read tables in PDF.

    Args:
        input_path (str, path object or file-like object):
            File like object of tareget PDF file.
            It can be URL, which is downloaded by tabula-py automatically.
        output_format (str, optional):
            Output format for returned object (``dataframe`` or ``json``)
        encoding (str, optional):
            Encoding type for pandas. Default: ``utf-8``
        java_options (list, optional):
            Set java options.

            Example:
                ``["-Xmx256m"]``
        pandas_options (dict, optional):
            Set pandas options.

            Example:
                ``{'header': None}``

            Note:
                With ``multiple_tables=True`` (default), pandas_options is passed
                to pandas.DataFrame, otherwise it is passed to pandas.read_csv.
                Those two functions are different for accept options like ``dtype``.
        multiple_tables (bool):
            It enables to handle multiple tables within a page. Default: ``True``

            Note:
                If `multiple_tables` option is enabled, tabula-py uses not
                :func:`pd.read_csv()`, but :func:`pd.DataFrame()`. Make
                sure to pass appropriate `pandas_options`.
        user_agent (str, optional):
            Set a custom user-agent when download a pdf from a url. Otherwise
            it uses the default ``urllib.request`` user-agent.
        kwargs:
            Dictionary of option for tabula-java. Details are shown in
            :func:`build_options()`

    Returns:
        list of DataFrames or dict.

    Raises:
        FileNotFoundError:
            If downloaded remote file doesn't exist.

        ValueError:
            If output_format is unknown format, or if downloaded remote file size is 0.

        tabula.errors.CSVParseError:
            If pandas CSV parsing failed.

        tabula.errors.JavaNotFoundError:
            If java is not installed or found.

        subprocess.CalledProcessError:
            If tabula-java execution failed.


    Examples:

        Here is a simple example.
        Note that :func:`read_pdf()` only extract page 1 by default.

        Notes:
            As of tabula-py 2.0.0, :func:`read_pdf()` sets `multiple_tables=True` by
            default. If you want to get consistent output with previous version, set
            `multiple_tables=False`.

        >>> import tabula
        >>> pdf_path = "https://github.com/chezou/tabula-py/raw/master/tests/resources/data.pdf"
        >>> tabula.read_pdf(pdf_path, stream=True)
        [             Unnamed: 0   mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear  carb
        0             Mazda RX4  21.0    6  160.0  110  3.90  2.620  16.46   0   1     4     4
        1         Mazda RX4 Wag  21.0    6  160.0  110  3.90  2.875  17.02   0   1     4     4
        2            Datsun 710  22.8    4  108.0   93  3.85  2.320  18.61   1   1     4     1
        3        Hornet 4 Drive  21.4    6  258.0  110  3.08  3.215  19.44   1   0     3     1
        4     Hornet Sportabout  18.7    8  360.0  175  3.15  3.440  17.02   0   0     3     2
        5               Valiant  18.1    6  225.0  105  2.76  3.460  20.22   1   0     3     1
        6            Duster 360  14.3    8  360.0  245  3.21  3.570  15.84   0   0     3     4
        7             Merc 240D  24.4    4  146.7   62  3.69  3.190  20.00   1   0     4     2
        8              Merc 230  22.8    4  140.8   95  3.92  3.150  22.90   1   0     4     2
        9              Merc 280  19.2    6  167.6  123  3.92  3.440  18.30   1   0     4     4
        10            Merc 280C  17.8    6  167.6  123  3.92  3.440  18.90   1   0     4     4
        11           Merc 450SE  16.4    8  275.8  180  3.07  4.070  17.40   0   0     3     3
        12           Merc 450SL  17.3    8  275.8  180  3.07  3.730  17.60   0   0     3     3
        13          Merc 450SLC  15.2    8  275.8  180  3.07  3.780  18.00   0   0     3     3
        14   Cadillac Fleetwood  10.4    8  472.0  205  2.93  5.250  17.98   0   0     3     4
        15  Lincoln Continental  10.4    8  460.0  215  3.00  5.424  17.82   0   0     3     4
        16    Chrysler Imperial  14.7    8  440.0  230  3.23  5.345  17.42   0   0     3     4
        17             Fiat 128  32.4    4   78.7   66  4.08  2.200  19.47   1   1     4     1
        18          Honda Civic  30.4    4   75.7   52  4.93  1.615  18.52   1   1     4     2
        19       Toyota Corolla  33.9    4   71.1   65  4.22  1.835  19.90   1   1     4     1
        20        Toyota Corona  21.5    4  120.1   97  3.70  2.465  20.01   1   0     3     1
        21     Dodge Challenger  15.5    8  318.0  150  2.76  3.520  16.87   0   0     3     2
        22          AMC Javelin  15.2    8  304.0  150  3.15  3.435  17.30   0   0     3     2
        23           Camaro Z28  13.3    8  350.0  245  3.73  3.840  15.41   0   0     3     4
        24     Pontiac Firebird  19.2    8  400.0  175  3.08  3.845  17.05   0   0     3     2
        25            Fiat X1-9  27.3    4   79.0   66  4.08  1.935  18.90   1   1     4     1
        26        Porsche 914-2  26.0    4  120.3   91  4.43  2.140  16.70   0   1     5     2
        27         Lotus Europa  30.4    4   95.1  113  3.77  1.513  16.90   1   1     5     2
        28       Ford Pantera L  15.8    8  351.0  264  4.22  3.170  14.50   0   1     5     4
        29         Ferrari Dino  19.7    6  145.0  175  3.62  2.770  15.50   0   1     5     6
        30        Maserati Bora  15.0    8  301.0  335  3.54  3.570  14.60   0   1     5     8
        31           Volvo 142E  21.4    4  121.0  109  4.11  2.780  18.60   1   1     4     2]

        If you want to extract all pages, set ``pages="all"``.

        >>> dfs = tabula.read_pdf(pdf_path, pages="all")
        >>> len(dfs)
        4
        >>> dfs
        [       0    1      2    3     4      5      6   7   8     9
        0    mpg  cyl   disp   hp  drat     wt   qsec  vs  am  gear
        1   21.0    6  160.0  110  3.90  2.620  16.46   0   1     4
        2   21.0    6  160.0  110  3.90  2.875  17.02   0   1     4
        3   22.8    4  108.0   93  3.85  2.320  18.61   1   1     4
        4   21.4    6  258.0  110  3.08  3.215  19.44   1   0     3
        5   18.7    8  360.0  175  3.15  3.440  17.02   0   0     3
        6   18.1    6  225.0  105  2.76  3.460  20.22   1   0     3
        7   14.3    8  360.0  245  3.21  3.570  15.84   0   0     3
        8   24.4    4  146.7   62  3.69  3.190  20.00   1   0     4
        9   22.8    4  140.8   95  3.92  3.150  22.90   1   0     4
        10  19.2    6  167.6  123  3.92  3.440  18.30   1   0     4
        11  17.8    6  167.6  123  3.92  3.440  18.90   1   0     4
        12  16.4    8  275.8  180  3.07  4.070  17.40   0   0     3
        13  17.3    8  275.8  180  3.07  3.730  17.60   0   0     3
        14  15.2    8  275.8  180  3.07  3.780  18.00   0   0     3
        15  10.4    8  472.0  205  2.93  5.250  17.98   0   0     3
        16  10.4    8  460.0  215  3.00  5.424  17.82   0   0     3
        17  14.7    8  440.0  230  3.23  5.345  17.42   0   0     3
        18  32.4    4   78.7   66  4.08  2.200  19.47   1   1     4
        19  30.4    4   75.7   52  4.93  1.615  18.52   1   1     4
        20  33.9    4   71.1   65  4.22  1.835  19.90   1   1     4
        21  21.5    4  120.1   97  3.70  2.465  20.01   1   0     3
        22  15.5    8  318.0  150  2.76  3.520  16.87   0   0     3
        23  15.2    8  304.0  150  3.15  3.435  17.30   0   0     3
        24  13.3    8  350.0  245  3.73  3.840  15.41   0   0     3
        25  19.2    8  400.0  175  3.08  3.845  17.05   0   0     3
        26  27.3    4   79.0   66  4.08  1.935  18.90   1   1     4
        27  26.0    4  120.3   91  4.43  2.140  16.70   0   1     5
        28  30.4    4   95.1  113  3.77  1.513  16.90   1   1     5
        29  15.8    8  351.0  264  4.22  3.170  14.50   0   1     5
        30  19.7    6  145.0  175  3.62  2.770  15.50   0   1     5
        31  15.0    8  301.0  335  3.54  3.570  14.60   0   1     5,               0            1             2            3        4
        0  Sepal.Length  Sepal.Width  Petal.Length  Petal.Width  Species
        1           5.1          3.5           1.4          0.2   setosa
        2           4.9          3.0           1.4          0.2   setosa
        3           4.7          3.2           1.3          0.2   setosa
        4           4.6          3.1           1.5          0.2   setosa
        5           5.0          3.6           1.4          0.2   setosa
        6           5.4          3.9           1.7          0.4   setosa,      0             1            2             3            4          5
        0  NaN  Sepal.Length  Sepal.Width  Petal.Length  Petal.Width    Species
        1  145           6.7          3.3           5.7          2.5  virginica
        2  146           6.7          3.0           5.2          2.3  virginica
        3  147           6.3          2.5           5.0          1.9  virginica
        4  148           6.5          3.0           5.2          2.0  virginica
        5  149           6.2          3.4           5.4          2.3  virginica
        6  150           5.9          3.0           5.1          1.8  virginica,        0
        0   supp
        1     VC
        2     VC
        3     VC
        4     VC
        5     VC
        6     VC
        7     VC
        8     VC
        9     VC
        10    VC
        11    VC
        12    VC
        13    VC
        14    VC]
    """  # noqa

    if output_format:
        # Respects explicit output_format
        multiple_tables = False

        if output_format.lower() == "dataframe":
            kwargs.pop("format", None)
        elif output_format.lower() == "json":
            kwargs["format"] = "JSON"
        else:
            raise ValueError("Unknown output_format {}".format(output_format))

    if multiple_tables:
        kwargs["format"] = "JSON"

    if java_options is None:
        java_options = []
    elif isinstance(java_options, str):
        java_options = shlex.split(java_options)

    # to prevent tabula-py from stealing focus on every call on mac
    if platform.system() == "Darwin":
        if not any("java.awt.headless" in opt for opt in java_options):
            java_options += ["-Djava.awt.headless=true"]

    if encoding == "utf-8":
        if not any("file.encoding" in opt for opt in java_options):
            java_options += ["-Dfile.encoding=UTF8"]

    path, temporary = localize_file(input_path, user_agent)

    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    if os.path.getsize(path) == 0:
        raise ValueError(
            "{} is empty. Check the file, or download it manually.".format(path)
        )

    try:
        output = _run(java_options, kwargs, path, encoding)
    finally:
        if temporary:
            os.unlink(path)

    if len(output) == 0:
        logger.warning("The output file is empty.")
        return []

    if pandas_options is None:
        pandas_options = {}

    fmt = kwargs.get("format")
    if fmt == "JSON":
        raw_json = json.loads(output.decode(encoding))
        if multiple_tables:
            return _extract_from(raw_json, pandas_options)
        else:
            return raw_json

    else:
        pandas_options["encoding"] = pandas_options.get("encoding", encoding)

        try:
            return [pd.read_csv(io.BytesIO(output), **pandas_options)]
        except pd.errors.ParserError as e:
            message = "Error failed to create DataFrame with different column tables.\n"
            message += (
                "Try to set `multiple_tables=True`"
                "or set `names` option for `pandas_options`. \n"
            )

            raise CSVParseError(message, e)


def read_pdf_with_template(
    input_path,
    template_path,
    pandas_options=None,
    encoding="utf-8",
    java_options=None,
    user_agent=None,
    **kwargs
):
    """Read tables in PDF with a Tabula App template.

    Args:
        input_path (str, path object or file-like object):
            File like object of target PDF file.
            It can be URL, which is downloaded by tabula-py automatically.
        template_path (str, path object or file-like object):
            File like object for Tabula app template.
            It can be URL, which is downloaded by tabula-py automatically.
        pandas_options (dict, optional):
            Set pandas options like {'header': None}.
        encoding (str, optional):
            Encoding type for pandas. Default is 'utf-8'
        java_options (list, optional):
            Set java options like ``["-Xmx256m"]``.
        user_agent (str, optional):
            Set a custom user-agent when download a pdf from a url. Otherwise
            it uses the default ``urllib.request`` user-agent.
        kwargs:
            Dictionary of option for tabula-java. Details are shown in
            :func:`build_options()`

    Returns:
        list of DataFrame.

    Raises:
        FileNotFoundError:
            If downloaded remote file doesn't exist.

        ValueError:
            If output_format is unknown format, or if downloaded remote file size is 0.

        tabula.errors.CSVParseError:
            If pandas CSV parsing failed.

        tabula.errors.JavaNotFoundError:
            If java is not installed or found.

        subprocess.CalledProcessError:
            If tabula-java execution failed.


    Examples:

        You can use template file extracted by tabula app.

        >>> import tabula
        >>> tabula.read_pdf_with_template(pdf_path, "/path/to/data.tabula-template.json")
        [             Unnamed: 0   mpg  cyl   disp   hp  ...   qsec  vs  am  gear  carb
        0             Mazda RX4  21.0    6  160.0  110  ...  16.46   0   1     4     4
        1         Mazda RX4 Wag  21.0    6  160.0  110  ...  17.02   0   1     4     4
        2            Datsun 710  22.8    4  108.0   93  ...  18.61   1   1     4     1
        3        Hornet 4 Drive  21.4    6  258.0  110  ...  19.44   1   0     3     1
        4     Hornet Sportabout  18.7    8  360.0  175  ...  17.02   0   0     3     2
        5               Valiant  18.1    6  225.0  105  ...  20.22   1   0     3     1
        6            Duster 360  14.3    8  360.0  245  ...  15.84   0   0     3     4
        7             Merc 240D  24.4    4  146.7   62  ...  20.00   1   0     4     2
        8              Merc 230  22.8    4  140.8   95  ...  22.90   1   0     4     2
        9              Merc 280  19.2    6  167.6  123  ...  18.30   1   0     4     4
        10            Merc 280C  17.8    6  167.6  123  ...  18.90   1   0     4     4
        11           Merc 450SE  16.4    8  275.8  180  ...  17.40   0   0     3     3
        12           Merc 450SL  17.3    8  275.8  180  ...  17.60   0   0     3     3
        13          Merc 450SLC  15.2    8  275.8  180  ...  18.00   0   0     3     3
        14   Cadillac Fleetwood  10.4    8  472.0  205  ...  17.98   0   0     3     4
        15  Lincoln Continental  10.4    8  460.0  215  ...  17.82   0   0     3     4
        16    Chrysler Imperial  14.7    8  440.0  230  ...  17.42   0   0     3     4
        17             Fiat 128  32.4    4   78.7   66  ...  19.47   1   1     4     1
        18          Honda Civic  30.4    4   75.7   52  ...  18.52   1   1     4     2
        19       Toyota Corolla  33.9    4   71.1   65  ...  19.90   1   1     4     1
        20        Toyota Corona  21.5    4  120.1   97  ...  20.01   1   0     3     1
        21     Dodge Challenger  15.5    8  318.0  150  ...  16.87   0   0     3     2
        22          AMC Javelin  15.2    8  304.0  150  ...  17.30   0   0     3     2
        23           Camaro Z28  13.3    8  350.0  245  ...  15.41   0   0     3     4
        24     Pontiac Firebird  19.2    8  400.0  175  ...  17.05   0   0     3     2
        25            Fiat X1-9  27.3    4   79.0   66  ...  18.90   1   1     4     1
        26        Porsche 914-2  26.0    4  120.3   91  ...  16.70   0   1     5     2
        27         Lotus Europa  30.4    4   95.1  113  ...  16.90   1   1     5     2
        28       Ford Pantera L  15.8    8  351.0  264  ...  14.50   0   1     5     4
        29         Ferrari Dino  19.7    6  145.0  175  ...  15.50   0   1     5     6
        30        Maserati Bora  15.0    8  301.0  335  ...  14.60   0   1     5     8
        31           Volvo 142E  21.4    4  121.0  109  ...  18.60   1   1     4     2
        [32 rows x 12 columns],
            0            1             2            3        4
        0  NaN  Sepal.Width  Petal.Length  Petal.Width  Species
        1  5.1          3.5           1.4          0.2   setosa
        2  4.9          3.0           1.4          0.2   setosa
        3  4.7          3.2           1.3          0.2   setosa
        4  4.6          3.1           1.5          0.2   setosa
        5  5.0          3.6           1.4          0.2   setosa,
            0             1            2             3            4          5
        0  NaN  Sepal.Length  Sepal.Width  Petal.Length  Petal.Width    Species
        1  145           6.7          3.3           5.7          2.5  virginica
        2  146           6.7          3.0           5.2          2.3  virginica
        3  147           6.3          2.5           5.0          1.9  virginica
        4  148           6.5          3.0           5.2          2.0  virginica
        5  149           6.2          3.4           5.4          2.3  virginica,
            Unnamed: 0 supp  dose
        0          4.2   VC   0.5
        1         11.5   VC   0.5
        2          7.3   VC   0.5
        3          5.8   VC   0.5
        4          6.4   VC   0.5
        5         10.0   VC   0.5
        6         11.2   VC   0.5
        7         11.2   VC   0.5
        8          5.2   VC   0.5
        9          7.0   VC   0.5
        10        16.5   VC   1.0
        11        16.5   VC   1.0
        12        15.2   VC   1.0
        13        17.3   VC   1.0]
    """  # noqa

    path, temporary = localize_file(
        template_path, user_agent=user_agent, suffix=".json"
    )
    options = load_template(path)
    dataframes = []

    try:
        for option in options:
            _df = read_pdf(
                input_path,
                pandas_options=pandas_options,
                encoding=encoding,
                java_options=java_options,
                **dict(kwargs, **option)
            )

            if isinstance(_df, list):
                dataframes.extend(_df)
            else:
                dataframes.append(_df)
    finally:
        if temporary:
            os.unlink(path)

    return dataframes


def convert_into(
    input_path, output_path, output_format="csv", java_options=None, **kwargs
):
    """Convert tables from PDF into a file.
    Output file will be saved into `output_path`.

    Args:
        input_path (file like obj):
            File like object of tareget PDF file.
        output_path (str):
            File path of output file.
        output_format (str, optional):
            Output format of this function (``csv``, ``json`` or ``tsv``).
            Default: ``csv``
        java_options (list, optional):
            Set java options

            Example:
                ``"-Xmx256m"``.
        kwargs:
            Dictionary of option for tabula-java. Details are shown in
            :func:`build_options()`

    Raises:
        FileNotFoundError:
            If downloaded remote file doesn't exist.

        ValueError:
            If output_format is unknown format, or if downloaded remote file size is 0.

        tabula.errors.JavaNotFoundError:
            If java is not installed or found.

        subprocess.CalledProcessError:
            If tabula-java execution failed.
    """

    if output_path is None or len(output_path) == 0:
        raise ValueError("'output_path' shoud not be None or empty")

    kwargs["output_path"] = output_path
    kwargs["format"] = _extract_format_for_conversion(output_format)

    java_options = _build_java_options(java_options)

    path, temporary = localize_file(input_path)

    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    if os.path.getsize(path) == 0:
        raise ValueError(
            "{} is empty. Check the file, or download it manually.".format(path)
        )

    try:
        _run(java_options, kwargs, path)
    finally:
        if temporary:
            os.unlink(path)


def convert_into_by_batch(input_dir, output_format="csv", java_options=None, **kwargs):
    """Convert tables from PDFs in a directory.

    Args:
        input_dir (str):
            Directory path.
        output_format (str, optional):
            Output format of this function (csv, json or tsv)
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        kwargs:
            Dictionary of option for tabula-java. Details are shown in
            :func:`build_options()`

    Returns:
        Nothing. Outputs are saved into the same directory with `input_dir`

    Raises:
        ValueError:
            If input_dir doesn't exist.

        tabula.errors.JavaNotFoundError:
            If java is not installed or found.

        subprocess.CalledProcessError:
            If tabula-java execution failed.
    """

    if input_dir is None or not os.path.isdir(input_dir):
        raise ValueError("'input_dir' should be an existing directory path")

    kwargs["format"] = _extract_format_for_conversion(output_format)

    java_options = _build_java_options(java_options)

    # Option for batch
    kwargs["batch"] = input_dir

    _run(java_options, kwargs)


def _build_java_options(_java_options=None):
    if _java_options is None:
        _java_options = []
    elif isinstance(_java_options, str):
        _java_options = shlex.split(_java_options)

    # to prevent tabula-py from stealing focus on every call on mac
    if platform.system() == "Darwin":
        r = "java.awt.headless"
        if not any(filter(r.find, _java_options)):
            _java_options = _java_options + ["-Djava.awt.headless=true"]

    return _java_options


def _extract_format_for_conversion(output_format="csv"):
    if output_format.lower() == "csv":
        return "CSV"
    elif output_format.lower() == "json":
        return "JSON"
    elif output_format.lower() == "tsv":
        return "TSV"
    else:
        raise ValueError("Unknown 'output_format': '{}'".format(output_format))


def _extract_from(raw_json, pandas_options=None):
    """Extract tables from json.

    Args:
        raw_json (list):
            Decoded list from tabula-java JSON.
        pandas_options (dict optional):
            pandas options for `pd.DataFrame()`
    """

    data_frames = []
    if pandas_options is None:
        pandas_options = {}

    columns = pandas_options.pop("columns", None)
    columns, header_line_number = _convert_pandas_csv_options(pandas_options, columns)

    for table in raw_json:
        if len(table["data"]) == 0:
            continue

        list_data = [
            [np.nan if not e["text"] else e["text"] for e in row]
            for row in table["data"]
        ]
        _columns = columns

        if isinstance(header_line_number, int) and not columns:
            _columns = list_data.pop(header_line_number)
            _unname_idx = 0
            for idx, col in enumerate(_columns):
                if col is np.nan:
                    _columns[idx] = "Unnamed: {}".format(_unname_idx)
                    _unname_idx += 1

            counts = defaultdict(int)

            # Avoid duplicate column name adding ".\d" as a suffix
            for idx, col in enumerate(_columns):
                cur_count = counts[col]

                while cur_count > 0:
                    counts[col] = cur_count + 1
                    col = "{}.{}".format(col, cur_count)
                    cur_count = counts[col]

                _columns[idx] = col
                counts[col] = cur_count + 1

        df = pd.DataFrame(data=list_data, columns=_columns, **pandas_options)

        if not pandas_options.get("dtype"):
            for c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="ignore")
        data_frames.append(df)

    return data_frames


def _convert_pandas_csv_options(pandas_options, columns):
    """Translate `pd.read_csv()` options into `pd.DataFrame()` especially for header.

    Args:
        pandas_options (dict):
            pandas options like {'header': None}.
        columns (list):
            list of column name.
    """

    _columns = pandas_options.pop("names", columns)
    header = pandas_options.pop("header", "infer")
    pandas_options.pop("encoding", None)

    if header == "infer":
        header_line_number = 0 if not bool(_columns) else None
    else:
        header_line_number = header

    return _columns, header_line_number


def build_options(
    pages=None,
    guess=True,
    area=None,
    relative_area=False,
    lattice=False,
    stream=False,
    password=None,
    silent=None,
    columns=None,
    format=None,
    batch=None,
    output_path=None,
    options="",
):
    """Build options for tabula-java

    Args:
        pages (str, int, `list` of `int`, optional):
            An optional values specifying pages to extract from. It allows
            `str`,`int`, `list` of :`int`. Default: `1`

            Examples:
                ``'1-2,3'``, ``'all'``, ``[1,2]``
        guess (bool, optional):
            Guess the portion of the page to analyze per page. Default `True`
            If you use "area" option, this option becomes `False`.

            Note:
                As of tabula-java 1.0.3, guess option becomes independent from
                lattice and stream option, you can use guess and lattice/stream option
                at the same time.

        area (list of float, list of list of float, optional):
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
        columns (list, optional):
            X coordinates of column boundaries.

            Example:
                ``[10.1, 20.2, 30.3]``
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

    Returns:
        list:
            Built list of options
    """

    __options = []
    # handle options described in string for backward compatibility
    __options += shlex.split(options)

    if pages:
        __pages = pages
        if isinstance(pages, int):
            __pages = str(pages)
        elif type(pages) in [list, tuple]:
            __pages = ",".join(map(str, pages))

        __options += ["--pages", __pages]
    else:
        logger.warning(
            "'pages' argument isn't specified."
            "Will extract only from page 1 by default."
        )

    multiple_areas = False

    if area:
        guess = False
        __area = area
        if type(area) in [list, tuple]:
            # Check if nested list or tuple for multiple areas
            if any(type(e) in [list, tuple] for e in area):
                for e in area:
                    __area = "{percent}{area_str}".format(
                        percent="%" if relative_area else "",
                        area_str=",".join(map(str, e)),
                    )
                    __options += ["--area", __area]
                    multiple_areas = True

            else:
                __area = "{percent}{area_str}".format(
                    percent="%" if relative_area else "",
                    area_str=",".join(map(str, area)),
                )
                __options += ["--area", __area]

    if lattice:
        __options.append("--lattice")

    if stream:
        __options.append("--stream")

    if guess and not multiple_areas:
        __options.append("--guess")

    if format:
        __options += ["--format", format]

    if output_path:
        __options += ["--outfile", output_path]

    if columns:
        __columns = ",".join(map(str, columns))
        __options += ["--columns", __columns]

    if password:
        __options += ["--password", password]

    if batch:
        __options += ["--batch", batch]

    if silent:
        __options.append("--silent")

    return __options
