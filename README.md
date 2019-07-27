# tabula-py

[![Build Status](https://travis-ci.org/chezou/tabula-py.svg?branch=master)](https://travis-ci.org/chezou/tabula-py)
[![PyPI version](https://badge.fury.io/py/tabula-py.svg)](https://badge.fury.io/py/tabula-py)
[![Patreon](https://img.shields.io/badge/patreon-donate-orange.svg)](https://www.patreon.com/chezou)


`tabula-py` is a simple Python wrapper of [tabula-java](https://github.com/tabulapdf/tabula-java), which can read table of PDF.
You can read tables from PDF and convert into pandas's DataFrame. tabula-py also enables you to convert a PDF file into CSV/TSV/JSON file.

You can see [the example notebook](https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb) and try it on Google Colab.

![](./example.png)


# Requirements

- Java
  - Confirmed working with Java 7, 8

## OS

I confirmed working on macOS and Ubuntu. But some people confirm it works on Windows 10. See also following the setting procedure.

# Usage

## Install

```bash
pip install tabula-py
```

If you want to become a contributor, you can install dependency after cloning the repo as follows:

```bash
pip install -e .[dev, test]
pip install nox
```

For running text and liter, run nox command.

```bash
nox .
```

## Example

tabula-py enables you to extract table from PDF into DataFrame and JSON. It also can extract tables from PDF and save file as CSV, TSV or JSON.

```py
import tabula

# Read pdf into DataFrame
df = tabula.read_pdf("test.pdf", pages='all')

# Read remote pdf into DataFrame
df2 = tabula.read_pdf("https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/arabic.pdf")

# convert PDF into CSV
tabula.convert_into("test.pdf", "output.csv", output_format="csv", pages='all')

# convert all PDFs in a directory
tabula.convert_into_by_batch("input_directory", output_format='csv', pages='all)
```

See [example notebook](./examples/tabula_example.ipynb) for more detail. I also recommend to read [the tutorial article](https://aegis4048.github.io/parse-pdf-files-while-retaining-structure-with-tabula-py) written by [@aegis4048](https://github.com/aegis4048).

## Get tabula-py working (Windows 10)

This instruction is originally written by [@lahoffm](https://github.com/lahoffm). Thanks!

- If you don't have it already, install [Java](https://www.java.com/en/download/manual.jsp)
- Try to run example code (replace the appropriate PDF file name).
- If there's a `FileNotFoundError` when it calls `read_pdf()`, and when you type `java` on command line it says
`'java' is not recognized as an internal or external command, operable program or batch file`, you should set `PATH` environment variable to point to the Java directory.
- Find the main Java folder like `jre...` or `jdk...`. On Windows 10 it was under `C:\Program Files\Java`
- On Windows 10: **Control Panel** -> **System and Security** -> **System** -> **Advanced System Settings** -> **Environment Variables** -> Select **PATH** --> **Edit**
- Add the `bin` folder like `C:\Program Files\Java\jre1.8.0_144\bin`, hit OK a bunch of times.
- On command line, `java` should now print a list of options, and `tabula.read_pdf()` should run.

## Options

- pages (str, int, `list` of `int`, optional)
  - An optional values specifying pages to extract from. It allows `str`, `int`, `list` of `int`.
  - Example: 1, '1-2,3', 'all' or [1,2]. Default is 1
- guess (bool, optional):
  - Guess the portion of the page to analyze per page. Default `True`
  - Note that as of tabula-java 1.0.3, guess option becomes independent from lattice and stream option, you can use guess and lattice/stream option at the same time.
- area (`list` of `float`, optional):
  - Portion of the page to analyze(top,left,bottom,right).
  - Example: `[269.875, 12.75, 790.5, 561]`  or `[[12.1,20.5,30.1,50.2],[1.0,3.2,10.5,40.2]]`. Default is entire page
- relative_area (bool, optional):
  - If all area values are between 0-100 (inclusive) and preceded by '%', input will be taken as % of actual height or width of the page. Default `False`.
- lattice (bool, optional):
  - (`spreadsheet` option is deprecated) Force PDF to be extracted using lattice-mode extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet).
- stream (bool, optional):
  - (`nospreadsheet` option is deprecated) Force PDF to be extracted using stream-mode extraction (if there are no ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
- password (bool, optional):
  - Password to decrypt document. Default is empty
- silent (bool, optional):
  - Suppress all stderr output.
- columns (list, optional):
  - X coordinates of column boundaries.
  - Example: `[10.1, 20.2, 30.3]`
- output_format (str, optional):
  - Format for output file or extracted object.
  - For `read_pdf()`: `json`, `dataframe`
  - For `convert_into()`: `csv`, `tsv`, `json`
- output_path (str, optional):
  - Output file path. File format of it is depends on `format`.
  - Same as `--outfile` option of tabula-java.
- java_options (`list`, optional):
  - Set java options like `-Xmx256m`.
- pandas_options (`dict`, optional):
  - Set pandas options like `{'header': None}`.
- multiple_tables (bool, optional):
  - Extract multiple tables.  If used with multiple pages (e.g. `pages='all'`) will extract separate tables from each page.
  - This option uses JSON as an intermediate format, so if tabula-java output format will change, this option doesn't work.
- user_agent (str, optional)
  - Set a custom user-agent when download a pdf from a url. Otherwise it uses the default urllib.request user-agent


## FAQ

### `tabula-py` does not work

There are several possible reasons, but `tabula-py` is just a wrapper of [`tabula-java`](https://github.com/tabulapdf/tabula-java), make sure you've installed Java and you can use `java` command on your terminal. Many issue reporters forget to set PATH for `java` command.

You can check whether tabula-py can call `java` from Python process with `tabula.environment_info()` function.

### I can't `from tabula import read_pdf`

If you've installed `tabula`, it will be conflict the namespace. You should install `tabula-py` after removing `tabula`.

```bash
pip uninstall tabula
pip install tabula-py
```

### The result is different from `tabula-java`. Or, `stream` option seems not to work appropreately

`tabula-py` set `guess` option `True` by default, for beginners. It is known to make a conflict between `stream` option. If you feel something strange with your result, please set `guess=False`.

### Can I use option `xxx`?

Yes. You can use `options` argument as following. The format is same as cli of tabula-java.

```python
read_pdf(file_path, options="--columns 10.1,20.2,30.3")
```

### How can I ignore useless area?

In short, you can extract with `area` and `spreadsheet` option.

```python
In [4]: tabula.read_pdf('./table.pdf', spreadsheet=True, area=(337.29, 226.49, 472.85, 384.91))
Picked up JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8
Out[4]:
  Unnamed: 0 Col2 Col3 Col4 Col5
0          A    B   12    R    G
1        NaN    R    T   23    H
2          B    B   33    R    A
3          C    T   99    E    M
4          D    I   12   34    M
5          E    I    I    W   90
6        NaN    1    2    W    h
7        NaN    4    3    E    H
8          F    E   E4    R    4
```

#### How to use `area` option

According to tabula-java wiki, there is a explain how to specify the area:
https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want

For example, using macOS's preview, I got area information of this [PDF](https://github.com/chezou/tabula-py/files/711877/table.pdf):

![image](https://cloud.githubusercontent.com/assets/916653/22047470/b201de24-dd6a-11e6-9cfc-7bc73e33e3b2.png)


```bash
java -jar ./target/tabula-1.0.1-jar-with-dependencies.jar -p all -a $y1,$x1,$y2,$x2 -o $csvfile $filename
```

given

```python
# Note the left, top, height, and width parameters and calculate the following:

y1 = top
x1 = left
y2 = top + height
x2 = left + width
```

I confirmed with tabula-java:

```bash
java -jar ./tabula/tabula-1.0.1-jar-with-dependencies.jar -a "337.29,226.49,472.85,384.91" table.pdf
```

Without `-r`(same as `--spreadsheet`) option, it does not work properly.

### I faced `ParserError: Error tokenizing data. C error`. How can I extract multiple tables?

This error occurs pandas trys to extract multiple tables with different column size at once.
Use `multiple_tables` option, then you can avoid this error.

### I want to prevent tabula-py from stealing focus on every call on my mac

Set `java_options=["-Djava.awt.headless=true"]`. kudos [@jakekara](https://twitter.com/jakekara/status/979031539697831937)

### I got `?` character with result on Windows. How can I avoid it?

If the encoding of PDF is UTF-8, you should set `chcp 65001` on your terminal before launching a Python process.

```sh
chcp 65001
```

Then you can extract UTF-8 PDF with `java_options="-Dfile.encoding=UTF8"` option. This option will be added with `encoding='utf-8'` option, which is also set by default.

```python
# This is an example for java_options is set explicitly
df = read_pdf(file_path, java_options="-Dfile.encoding=UTF8")
```

Replace `65001` and `UTF-8` appropriately, if the file encoding isn't UTF-8.

### I can't extract file/directory name with space on Windows

You should escape file/directory name yourself.


### I want to use a different tabula .jar  file
You can specify the jar location via enviroment variable
```bash
export TABULA_JAR=".../tabula-x.y.z-jar-with-dependencies.jar"
```

### I want to extract multiple tables from a document
You can use the following example code
```
df = read_pdf(file_path, multiple_tables=True)
```
The result will be a list of DataFrames.  If you want separate tables across all pages in a document, use the `pages` argument.

### Table cell contents sometimes overflow into the next row.
You can try using `lattice=True`, which will often work if there are lines separating cells in the table.


## Contributing

Interested in helping out? I'd love to have your help!

You can help by:

- [Reporting a bug](https://github.com/tabulapdf/tabula-py/issues).
- Adding or editing documentation.
- Contributing code via a Pull Request.
- Write a blog post or spreading the word about `tabula-py` to people who might be able to benefit from using it.


### Contributors

- [@lahoffm](https://github.com/lahoffm)
- [@jakekara](https://github.com/jakekara)
- [@lcd1232](https://github.com/lcd1232)
- [@kirkholloway](https://github.com/kirkholloway)
- [@CurtLH](https://github.com/CurtLH)
- [@nikhilgk](https://github.com/nikhilgk)
- [@krassowski](https://github.com/krassowski)
- [@alexandreio](https://github.com/alexandreio)
- [@rmnevesLH](https://github.com/rmnevesLH)
- [@red-bin](https://github.com/red-bin)
- [@Gallaecio](https://github.com/Gallaecio)

### Another support

You can also support our continued work on `tabula-py` with a donation [on Patreon](https://www.patreon.com/chezou).
