'''This module is a wrapper of tabula, which enables extract tables from PDF.

This module extract tables from PDF into pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Todo:
  * Use py4j and handle multiple tables in a page

'''

import io
import json
import os
import shlex
import subprocess
import requests
import pandas as pd
import numpy as np
from .util import deprecated

JAR_NAME = "tabula-0.9.2-jar-with-dependencies.jar"
JAR_DIR = os.path.abspath(os.path.dirname(__file__))
JAR_PATH = os.path.join(JAR_DIR, JAR_NAME)

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
        java_options = [java_options]

    options = build_options(kwargs)
    path, is_url = localize_file(input_path)
    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [path]

    try:
        output = subprocess.check_output(args)
    finally:
        if is_url:
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

        return pd.read_csv(io.BytesIO(output), **pandas_options)


# Set alias for future rename from `read_pdf_table` to `read_pdf`
read_pdf_table = deprecated(read_pdf)


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
        java_options = [java_options]

    options = build_options(kwargs)
    path, is_url = localize_file(input_path)
    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [path]

    try:
        subprocess.check_output(args)
    finally:
        if is_url:
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
        java_options = [java_options]

    # Option for batch
    kwargs['batch'] = input_dir

    options = build_options(kwargs)

    args = ["java"] + java_options + ["-jar", JAR_PATH] + options

    subprocess.check_output(args)


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


def localize_file(path):
    '''Ensure localize target file.

    If the target file is remote, this function fetches into local storage.

    Args:
        path (str):
            File path or URL of target file.
    '''

    is_url = False
    try:
        pid = os.getpid()
        r = requests.get(path)
        filename = os.path.basename(r.url)
        if os.path.splitext(filename)[-1] is not ".pdf":
            filename = "{0}.pdf".format(pid)

        with open(filename, 'wb') as f:
            f.write(r.content)

        is_url = True
        return filename, is_url

    except:
        return path, is_url


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
            Guess the portion of the page to analyze per page.
        area (:obj:`list` of :obj:`float`, optional):
            Portion of the page to analyze(top,left,bottom,right).
            Example: [269.875,12.75,790.5,561]. Default is entire page
        spreadsheet (bool, optional):
            Force PDF to be extracted using spreadsheet-style extraction
            (if there are ruling lines separating each cell, as in a PDF of an
            Excel spreadsheet)
        nospreadsheet (bool, optional):
            Force PDF not to be extracted using spreadsheet-style extraction
            (if there are ruling lines separating each cell, as in a PDF of an
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
        Built dictionary of options
    '''
    __options = []
    if kwargs is None:
        kwargs = {}
    options = kwargs.get('options', '')
    # handle options described in string for backward compatibility
    __options += shlex.split(options)

    # parse options
    pages = kwargs.get('pages', 1)
    if pages:
        __pages = pages
        if isinstance(pages, int):
            __pages = str(pages)
        elif type(pages) in [list, tuple]:
            __pages = ",".join(map(str, pages))

        __options += ["--pages", __pages]

    guess = kwargs.get('guess', True)
    if guess:
        __options.append("--guess")

    area = kwargs.get('area')
    if area:
        __area = area
        if type(area) in [list, tuple]:
            __area = ",".join(map(str, area))

        __options += ["--area", __area]

    fmt = kwargs.get('format')
    if fmt:
        __options += ["--format", fmt]

    output_path = kwargs.get('output_path')
    if output_path:
        __options += ["--outfile", output_path]

    spreadsheet = kwargs.get('spreadsheet')
    if spreadsheet:
        __options.append("--spreadsheet")

    nospreadsheet = kwargs.get('nospreadsheet')
    if nospreadsheet:
        __options.append("--no-spreadsheet")

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
