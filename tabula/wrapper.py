'''This module is a wrapper of tabula, which enables extract tables from PDF.

This module extract tables from PDF into pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Todo:
  * Use py4j and handle multiple tables in a page

'''

import io
import json
import os
import platform
import shlex
import subprocess

import numpy as np
import pandas as pd
import shutil
import sys
import errno

from .util import deprecated_option

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

if PY3:
    from urllib.request import urlopen
    from urllib.parse import urlparse as parse_url
    from urllib.parse import uses_relative, uses_netloc, uses_params
    text_type = str
else:
    from urllib2 import urlopen
    from urlparse import urlparse as parse_url
    from urlparse import uses_relative, uses_netloc, uses_params
    text_type = unicode


_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
_VALID_URLS.discard('')


TABULA_JAVA_VERSION = "1.0.2"
JAR_NAME = "tabula-{}-jar-with-dependencies.jar".format(TABULA_JAVA_VERSION)
JAR_DIR = os.path.abspath(os.path.dirname(__file__))
JAR_PATH = os.path.join(JAR_DIR, JAR_NAME)

JAVA_NOT_FOUND_ERROR = "`java` command is not found from this Python process. Please ensure Java is installed and PATH is set for `java`"


# TODO: Remove this Python 2 compatibility code if possible
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def read_pdf(input_path,
             output_format='dataframe',
             encoding='utf-8',
             java_options=None,
             pandas_options=None,
             multiple_tables=False, **kwargs):
    '''Read tables in PDF.

    Args:
        input_path (str):
            File path of tareget PDF file.
        output_format (str, optional):
            Output format of this function (dataframe or json)
        encoding (str, optional):
            Encoding type for pandas. Default is 'utf-8'
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        pandas_options (dict, optional):
            Set pandas options like {'header': None}.
        multiple_tables (bool, optional):
            This is experimental option. It enables to handle multple tables within a page.
            Note: If `multiple_tables` option is enabled, tabula-py uses not `pd.read_csv()`,
             but `pd.DataFrame()`. Make sure to pass appropreate `pandas_options`.
        kwargs (dict):
            Dictionary of option for tabula-java. Details are shown in `build_options()`

    Returns:
        Extracted pandas DataFrame or list.
    '''

    if output_format == 'dataframe':
        kwargs.pop('format', None)

    elif output_format == 'json':
        kwargs['format'] = 'JSON'

    if multiple_tables:
        kwargs['format'] = 'JSON'

    if java_options is None:
        java_options = []

    elif isinstance(java_options, str):
        java_options = shlex.split(java_options)

    # to prevent tabula-py from stealing focus on every call on mac
    if platform.system() == 'Darwin':
        r = 'java.awt.headless'
        if not any(filter(r.find, java_options)):
            java_options = java_options + ['-Djava.awt.headless=true']

    if encoding == 'utf-8':
        r = 'file.encoding'
        if not any(filter(r.find, java_options)):
            java_options = java_options + ['-Dfile.encoding=UTF8']

    options = build_options(kwargs)

    path, temporary = _localize_file(input_path)
    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [path]

    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    try:
        output = subprocess.check_output(args)

    except FileNotFoundError as e:
        sys.stderr.write("Error: {}".format(e))
        sys.stderr.write("Error: {}".format(JAVA_NOT_FOUND_ERROR))
        raise

    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error: {}".format(e.output.decode(encoding)))
        raise

    finally:
        if temporary:
            os.unlink(path)

    if len(output) == 0:
        return

    if pandas_options is None:
        pandas_options = {}

    fmt = kwargs.get('format')
    if fmt == 'JSON':
        if multiple_tables:
            return extract_from(json.loads(output.decode(encoding)), pandas_options)

        else:
            return json.loads(output.decode(encoding))

    else:
        pandas_options['encoding'] = pandas_options.get('encoding', encoding)

        try:
            return pd.read_csv(io.BytesIO(output), **pandas_options)

        except pd.errors.ParserError as e:
            sys.stderr.write("Error: Failed to create DataFrame with different column tables.\n")
            sys.stderr.write("Error: Try to set `multiple_tables=True`.\n")
            raise


def convert_into(input_path, output_path, output_format='csv', java_options=None, **kwargs):
    '''Convert tables from PDF into a file.

    Args:
        input_path (str):
            File path of tareget PDF file.
        output_path (str):
            File path of output file.
        output_format (str, optional):
            Output format of this function (csv, json or tsv). Default: csv
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        kwargs (dict):
            Dictionary of option for tabula-java. Details are shown in `build_options()`

    Returns:
        Nothing. Output file will be saved into `output_path`
    '''

    if output_path is None or len(output_path) is 0:
        raise AttributeError("'output_path' shoud not be None or empty")

    kwargs['output_path'] = output_path
    kwargs['format'] = extract_format_for_conversion(output_format)

    if java_options is None:
        java_options = []

    elif isinstance(java_options, str):
        java_options = shlex.split(java_options)

    options = build_options(kwargs)
    path, temporary = _localize_file(input_path)
    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [path]

    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    try:
        subprocess.check_output(args)

    except FileNotFoundError as e:
        sys.stderr.write("Error: {}\n".format(e))
        sys.stderr.write("Error: {}\n".format(JAVA_NOT_FOUND_ERROR))
        raise

    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error: {}\n".format(e.output))
        raise

    finally:
        if temporary:
            os.unlink(path)


def convert_into_by_batch(input_dir, output_format='csv', java_options=None, **kwargs):
    '''Convert tables from PDFs in a directory.

    Args:
        input_dir (str):
            Directory path.
        output_format (str, optional):
            Output format of this function (csv, json or tsv)
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        kwargs (dict):
            Dictionary of option for tabula-java. Details are shown in `build_options()`

    Returns:
        Nothing. Outputs are saved into the same directory with `input_dir`
    '''

    if input_dir is None or not os.path.isdir(input_dir):
        raise AttributeError("'input_dir' shoud be directory path")

    kwargs['format'] = extract_format_for_conversion(output_format)

    if java_options is None:
        java_options = []

    elif isinstance(java_options, str):
        java_options = shlex.split(java_options)

    # Option for batch
    kwargs['batch'] = input_dir

    options = build_options(kwargs)

    args = ["java"] + java_options + ["-jar", JAR_PATH] + options

    try:
        subprocess.check_output(args)

    except FileNotFoundError as e:
        print("Error: {}".format(e))
        print("Error: {}".format(JAVA_NOT_FOUND_ERROR))
        raise

    except subprocess.CalledProcessError as e:
        print("Error: {}".format(e.output))
        raise


def extract_format_for_conversion(output_format='csv'):
    if output_format == 'csv':
        return 'CSV'

    if output_format == 'json':
        return 'JSON'

    if output_format == 'tsv':
        return 'TSV'

    if output_format == 'dataframe':
        raise AttributeError("'output_format' has no attribute 'dataframe'")


def extract_from(raw_json, pandas_options=None):
    '''Extract tables from json.

    Args:
        raw_json (list):
            Decoded list from tabula-java JSON.
        pandas_options (dict optional):
            pandas options for `pd.DataFrame()`
    '''

    data_frames = []
    if pandas_options is None:
        pandas_options = {}

    columns = pandas_options.pop('columns', None)
    columns, header_line_number = convert_pandas_csv_options(pandas_options, columns)

    for table in raw_json:
        list_data = [[np.nan if not e['text'] else e['text'] for e in row] for row in table['data']]
        _columns = columns

        if isinstance(header_line_number, int) and not columns:
            _columns = list_data.pop(header_line_number)
            _columns = ['' if e is np.nan else e for e in _columns]

        data_frames.append(pd.DataFrame(data=list_data, columns=_columns, **pandas_options))

    return data_frames


def convert_pandas_csv_options(pandas_options, columns):
    ''' Translate `pd.read_csv()` options into `pd.DataFrame()` especially for header.

    Args:
        pandas_option (dict):
            pandas options like {'header': None}.
        columns (list):
            list of column name.
    '''

    _columns = pandas_options.pop('names', columns)
    header = pandas_options.pop('header', None)

    if header == 'infer':
        header_line_number = 0 if not bool(_columns) else None
    else:
        header_line_number = header

    return _columns, header_line_number


def _localize_file(path_or_buffer):
    '''Ensure localize target file.

    If the target file is remote, this function fetches into local storage.

    Args:
        path (str):
            File path or file like object or URL of target file.
    
    Returns:
        filename (str): file name in local storage
        temporary_file_flag (bool): temporary file flag
    '''

    path_or_buffer = _stringify_path(path_or_buffer)

    if _is_url(path_or_buffer):
        req = urlopen(path_or_buffer)
        filename = os.path.basename(req.geturl())
        if os.path.splitext(filename)[-1] is not ".pdf":
            pid = os.getpid()
            filename = "{0}.pdf".format(pid)

        with open(filename, 'wb') as f:
            shutil.copyfileobj(req, f)

        return filename, True

    elif _is_file_like(path_or_buffer):
        pid = os.getpid()
        filename = "{0}.pdf".format(pid)

        with open(filename, 'wb') as f:
            shutil.copyfileobj(path_or_buffer, f)

        return filename, True

    # File path case
    else:
        return os.path.expanduser(path_or_buffer), False


def _is_url(url):
    try:
        return parse_url(url).scheme in _VALID_URLS

    except Exception:
        return False


def _is_file_like(obj):
    '''Check file like object

    Args:
        obj:
            file like object.
    
    Returns:
        bool: file like object or not
    '''

    if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
        return False

    if not hasattr(obj, "__iter__"):
        return False

    return True


def _stringify_path(path_or_buffer):
    '''Convert path like object to string

    Args:
        path_or_buffer: object to be converted

    Returns:
        string_path_or_buffer: maybe string version of path_or_buffer
    '''

    try:
        import pathlib
        _PATHLIB_INSTALLED = True
    except ImportError:
        _PATHLIB_INSTALLED = False

    if hasattr(path_or_buffer, '__fspath__'):
        return path_or_buffer.__fspath__()

    if _PATHLIB_INSTALLED and isinstance(path_or_buffer, pathlib.Path):
        return text_type(path_or_buffer)

    return path_or_buffer


def build_options(kwargs=None):
    '''Build options for tabula-java

    Args:
        options (str, optional):
            Raw option string for tabula-java.
        pages (str, int, :obj:`list` of :obj:`int`, optional):
            An optional values specifying pages to extract from. It allows
            `str`,`int`, :obj:`list` of :obj:`int`.
            Example: '1-2,3', 'all' or [1,2]
        guess (bool, optional):
            Guess the portion of the page to analyze per page. Default `True`
        area (:obj:`list` of :obj:`float` or :obj:`list` of :obj:`list` of :obj:`float`, optional):
            Portion of the page to analyze(top,left,bottom,right).
            Example: [269.875,12.75,790.5,561] or [[12.1,20.5,30.1,50.2],[1.0,3.2,10.5,40.2]].
            Default is entire page
        relative_area (bool, optional):
            If all area values are between 0-100 (inclusive) and preceded by '%', input will be taken as
            % of actual height or width of the page. Default False.
        lattice (bool, optional):
            Force PDF to be extracted using lattice-mode extraction
            (if there are ruling lines separating each cell, as in a PDF of an
            Excel spreadsheet)
        stream (bool, optional):
            Force PDF to be extracted using stream-mode extraction
            (if there are no ruling lines separating each cell, as in a PDF of an
             Excel spreadsheet)
        password (str, optional):
            Password to decrypt document. Default is empty
        silent (bool, optional):
            Suppress all stderr output.
        columns (list, optional):
            X coordinates of column boundaries.
            Example: [10.1, 20.2, 30.3]
        format (str, optional):
            Format for output file or extracted object. (CSV, TSV, JSON)
        batch (str, optional):
            Convert all .pdfs in the provided directory. This argument should be direcotry.
        output_path (str, optional):
            Output file path. File format of it is depends on `format`.
            Same as `--outfile` option of tabula-java.

    Returns:
        `obj`:list: Built list of options
    '''
    __options = []
    if kwargs is None:
        kwargs = {}
    options = kwargs.get('options', '')
    # handle options described in string for backward compatibility
    __options += shlex.split(options)

    DEPRECATED_OPTIONS = ['spreadsheet', 'nospreadsheet']
    for option in kwargs.keys() and DEPRECATED_OPTIONS:
        deprecated_option(option)

    # parse options
    pages = kwargs.get('pages', 1)
    if pages:
        __pages = pages
        if isinstance(pages, int):
            __pages = str(pages)
        elif type(pages) in [list, tuple]:
            __pages = ",".join(map(str, pages))

        __options += ["--pages", __pages]

    area = kwargs.get('area')
    relative_area = kwargs.get('relative_area')
    multiple_areas = False
    if area:
        __area = area
        if type(area) in [list, tuple]:
            # Check if nested list or tuple for multiple areas
            if any(type(e) in [list, tuple] for e in area):
                for e in area:
                    __area = "{percent}{area_str}".format(percent='%' if relative_area else '', area_str=",".join(map(str, e)))
                    __options += ["--area", __area]
                    multiple_areas = True

            else:
                __area = "{percent}{area_str}".format(percent='%' if relative_area else '', area_str=",".join(map(str, area)))
                __options += ["--area", __area]

    guess = kwargs.get('guess', True)
    if guess and not multiple_areas:
        __options.append("--guess")

    fmt = kwargs.get('format')
    if fmt:
        __options += ["--format", fmt]

    output_path = kwargs.get('output_path')
    if output_path:
        __options += ["--outfile", output_path]

    lattice = kwargs.get('lattice') or kwargs.get('spreadsheet')
    if lattice:
        __options.append("--lattice")

    stream = kwargs.get('stream') or kwargs.get('nospreadsheet')
    if stream:
        __options.append("--stream")

    columns = kwargs.get('columns')
    if columns:
        __columns = ",".join(map(str, columns))
        __options += ["--columns", __columns]

    password = kwargs.get('password')
    if password:
        __options += ["--password", password]

    batch = kwargs.get('batch')
    if batch:
        __options += ["--batch", batch]

    silent = kwargs.get('silent')
    if silent:
        __options.append("--silent")

    return __options
