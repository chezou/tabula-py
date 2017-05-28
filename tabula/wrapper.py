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

def read_pdf(input_path, **kwargs):
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
        kwargs (dict):
            Dictionary of option for tabula-java. Details are shown in `build_options()`

    Returns:
        Extracted pandas DataFrame or list.
    '''

    output_format = kwargs.get('output_format', 'dataframe')

    if output_format == 'dataframe':
        kwargs.pop('format', None)

    elif output_format == 'json':
        kwargs['format'] = 'JSON'

    multiple_tables = kwargs.get('multiple_tables')
    if multiple_tables:
        kwargs.pop('multiple_tables', None)
        kwargs['format'] = 'JSON'

    java_options = kwargs.get('java_options', [])
    if isinstance(java_options, str):
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

    encoding = kwargs.get('encoding', 'utf-8')

    fmt = kwargs.get('format')
    if fmt == 'JSON':
        if multiple_tables:
            return extract_from(json.loads(output.decode(encoding)))

        else:
            return json.loads(output.decode(encoding))

    else:
        return pd.read_csv(io.BytesIO(output), encoding=encoding)


# Set alias for future rename from `read_pdf_table` to `read_pdf`
read_pdf_table = deprecated(read_pdf)


def convert_into(input_path, output_path, **kwargs):
    '''Convert tables from PDF into a file.

    Args:
        input_path (str):
            File path of tareget PDF file.
        output_path (str):
            File path of output file.
        output_format (str, optional):
            Output format of this function (csv, json or tsv)
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
    kwargs['format'] = extract_format_for_conversion(kwargs.get('output_format'))

    java_options = kwargs.get('java_options', [])
    if isinstance(java_options, str):
        java_options = [java_options]

    options = build_options(kwargs)
    path, is_url = localize_file(input_path)
    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [path]

    try:
        subprocess.check_output(args)
    finally:
        if is_url:
            os.unlink(path)

def convert_into_by_batch(input_dir, **kwargs):
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

    kwargs['format'] = extract_format_for_conversion(kwargs.get('output_format'))

    java_options = kwargs.get('java_options', [])
    if isinstance(java_options, str):
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


def extract_from(raw_json):
    '''Extract tables from json.

    Args:
        raw_json (list):
            Decoded list from tabula-java JSON.
    '''

    data_frames = []

    for table in raw_json:
        list_data = [[np.nan if not e['text'] else e['text'] for e in row] for row in table['data']]
        data_frames.append(pd.DataFrame(list_data))

    return data_frames

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


def build_options(kwargs={}):
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
