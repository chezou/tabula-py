'''This module is a wrapper of tabula, which enables extract tables from PDF.

This module extract tables from PDF into pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Todo:
  * Use py4j and handle multiple tables in a page

'''

import subprocess
import io
import shlex
import os
import pandas as pd
import json

JAR_NAME = "tabula-0.9.1-jar-with-dependencies.jar"
jar_dir = os.path.abspath(os.path.dirname(__file__))
jar_path = os.path.join(jar_dir, JAR_NAME)


def read_pdf_table(input_path, **kwargs):
    '''Read tables in PDF.

    Args:
        input_path (str):
            File path of tareget PDF file.
        options (str, optional):
            Option string for tabula-java.
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
        password (bool, optional):
            Password to decrypt document. Default is empty
        silent (bool, optional):
            Suppress all stderr output.

    Returns:
        Extracted pandas DataFrame or list.
    '''

    output_format = kwargs.get('output_format', 'dataframe')

    if output_format == 'dataframe':
        kwargs.pop('format', None)

    elif output_format == 'json':
        kwargs['format'] = 'JSON'

    options = build_options(kwargs)
    args = ["java", "-jar", jar_path] + options + [input_path]

    output = subprocess.check_output(args)

    if len(output) == 0:
        return

    fmt = kwargs.get('format')
    if fmt == 'JSON':
        return json.loads(output.decode('utf-8'))

    else:
        return pd.read_csv(io.BytesIO(output))


# Set alias for future rename from `read_pdf_table` to `read_pdf`
read_pdf = read_pdf_table


def build_options(kwargs={}):
    __options = []
    options = kwargs.get('options', '')
    # handle options described in string for backward compatibility
    __options += shlex.split(options)

    # parse options
    pages = kwargs.get('pages', 1)
    if pages:
        __pages = pages
        if type(pages) == int:
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

    password = kwargs.get('password')
    if password:
        __options += ["--password", password]

    silent = kwargs.get('silent')
    if silent:
        __options.append("--silent")

    return __options
