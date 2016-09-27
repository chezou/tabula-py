'''This module is a wrapper of tabula, which enables extract tables from PDF.

This module extract tables from PDF into pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Todo:
  * Use py4j and handle multiple tables in a page

'''

import subprocess, io, shlex, os
import pandas as pd

JAR_NAME = "tabula-0.9.1-jar-with-dependencies.jar"
jar_dir = os.path.abspath(os.path.dirname(__file__))
jar_path = os.path.join(jar_dir, JAR_NAME)

def read_pdf_table(input_path, options="", pages=1, guess=True, area=None, spreadsheet=None, password=None, nospreadsheet=None, silent=None):
  '''Read tables in PDF.

  Args:
    input_path (str): File path of tareget PDF file.
    options (str, optional): Option string for tabula-java.
    pages (str, int, :obj:`list` of :obj:`int`, optional): An optional values specifying pages to extract from. It allows `str`, `int`, :obj:`list` of :obj:`int`. Example: '1-2,3', 'all' or [1,2]
    guess (bool, optional): Guess the portion of the page to analyze per page.
    area (:obj:`list` of :obj:`float`, optional): Portion of the page to analyze(top,left,bottom,right). Example: [269.875,12.75,790.5,561]. Default is entire page
    spreadsheet (bool, optional): Force PDF to be extracted using spreadsheet-style extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
    nospreadsheet (bool, optional): Force PDF not to be extracted using spreadsheet-style extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
    password (bool, optional): Password to decrypt document. Default is empty
    silent (bool, optional): Suppress all stderr output.

  Returns:
    Extracted pandas DataFrame.
  '''

  __options = []
  # handle options described in string for backward compatibility
  __options += shlex.split(options)

  # parse options
  if pages:
    __pages = pages
    if type(pages) == int:
      __pages = str(pages)
    elif type(pages) in [list, tuple]:
      __pages = ",".join(map(str, pages))

    __options += ["--pages", __pages]

  if guess:
    __options.append("--guess")

  if area:
    __area = area
    if type(area) in [list, tuple]:
      __area = ",".join(map(str, area))

    __options += ["--area", __area]

  if spreadsheet:
    __options.append("--spreadsheet")

  if nospreadsheet:
    __options.append("--no-spreadsheet")

  if password:
    __options += ["--password", password]

  if silent:
    __options.append("--silent")

  args = ["java", "-jar", jar_path] + __options + [input_path]

  output = subprocess.check_output(
    args,
    stderr=subprocess.STDOUT)

  if len(output) == 0:
    return

  return pd.read_csv(io.BytesIO(output))
