import subprocess, io, shlex, os
import pandas as pd

JAR_NAME = "tabula-0.9.1-jar-with-dependencies.jar"
jar_dir = os.path.abspath(os.path.dirname(__file__))
jar_path = os.path.join(jar_dir, JAR_NAME)

def read_pdf_table(input_path, options="", pages=1, guess=True, area=None, spreadsheet=None, password=None, nospreadsheet=None, silent=None):

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

  result = subprocess.run(args, stdout=subprocess.PIPE)

  if len(result.stdout) == 0:
    return

  return pd.read_csv(io.BytesIO(result.stdout))
