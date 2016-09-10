import subprocess, io, shlex, os
import pandas as pd

def read_pdf_table(input_path, options=""):
  JAR_NAME = "tabula-0.9.1-jar-with-dependencies.jar"
  jar_dir = os.path.abspath(os.path.dirname(__file__))
  jar_path = os.path.join(jar_dir, JAR_NAME)
  args = ["java", "-jar", jar_path] + shlex.split(options) + [input_path]

  result = subprocess.run(args, stdout=subprocess.PIPE)

  if len(result.stdout) == 0:
    return

  return pd.read_csv(io.BytesIO(result.stdout))
