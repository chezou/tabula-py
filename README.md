# tabula-py

[![Build Status](https://travis-ci.org/chezou/tabula-py.svg?branch=master)](https://travis-ci.org/chezou/tabula-py)

`tabula-py` is a simple Python wrapper of [tabula-java](https://github.com/tabulapdf/tabula-java), which can read table of PDF.
You can read tables from PDF and convert into pandas's DataFrame.

![](http://i.imgur.com/ODM8hst.jpg)


# Requirements

- Java
  - Confirmed working with Java 7, 8
- pandas

## OS

I confirmed working on macOS and Ubuntu. I can't fully support Windows environment.

# Usage

## Install

```
pip install tabula-py
```

If you want to become a contributor, you can install dependency for development of tabula-py as follows:

```
pip install -r requirements.txt -c constraints.txt
```

## Example

tabula-py enables you to extract table from PDF into DataFrame and JSON. It also can extract tables from PDF and save file as CSV, TSV or JSON.

```py
import tabula

# Read pdf into DataFrame
df = tabula.read_pdf("test.pdf", options)

# Read remote pdf into DataFrame
df2 = tabula.read_pdf("https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/arabic.pdf")

# convert PDF into CSV
tabula.convert_into("test.pdf", "output.csv", output_format="csv")

# convert all PDFs in a directory
tabula.convert_into_by_batch("input_directory", output_format='csv')
```

See [example notebook](./examples/tabula_example.ipynb)

## Options

- pages (str, int, `list` of `int`, optional)
  - An optional values specifying pages to extract from. It allows `str`, `int`, `list` of `int`.
  - Example: 1, '1-2,3', 'all' or [1,2]. Default is 1
- guess (bool, optional):
  - Guess the portion of the page to analyze per page.
- area (`list` of `float`, optional):
  - Portion of the page to analyze(top,left,bottom,right).
  - Example: [269.875, 12.75, 790.5, 561]. Default is entire page
- lattice (bool, optional):
  - [`spreadsheet` option is deprecated] Force PDF to be extracted using lattice-mode extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet). 
- stream (bool, optional):
  - [`nospreadsheet` option is deprecated] Force PDF to be extracted using stream-mode extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
- password (bool, optional):
  - Password to decrypt document. Default is empty
- silent (bool, optional):
  - Suppress all stderr output.
- columns (list, optional):
  - X coordinates of column boundaries.
  - Example: [10.1, 20.2, 30.3]
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
  - (Experimental) Extract multiple tables. 
  - This option uses JSON as an intermediate format, so if tabula-java output format will change, this option doesn't work.


## FAQ

### I can't `from tabula import read_pdf`

If you've installed `tabula`, it will be conflict the namespace. You should install `tabula-py` after removing `tabula`.

```
pip uninstall tabula
pip install tabula-py
```


### Can I use option `xxx`?

Yes. You can use `options` argument as following. The format is same as cli of tabula-java.

```py
read_pdf_table(file_path, options="--columns 10.1,20.2,30.3")
```

### How can I ignore useless area?

In short, you can extract with `area` and `spreadsheet` option.

```py
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

*How to use `area` option*

According to tabula-java wiki, there is a explain how to specify the area:
https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want

For example, using macOS's preview, I got area information of this [PDF](https://github.com/chezou/tabula-py/files/711877/table.pdf):

![image](https://cloud.githubusercontent.com/assets/916653/22047470/b201de24-dd6a-11e6-9cfc-7bc73e33e3b2.png)


```
java -jar ./target/tabula-1.0.1-jar-with-dependencies.jar -p all -a $y1,$x1,$y2,$x2 -o $csvfile $filename
```

given

```
Note the left, top, height, and width parameters and calculate the following:

y1 = top
x1 = left
y2 = top + height
x2 = left + width
```

I confirmed with tabula-java:

```
java -jar ./tabula/tabula-1.0.1-jar-with-dependencies.jar -a "337.29,226.49,472.85,384.91" table.pdf
```

Without `-r`(same as `--spreadsheet`) option, it does not work properly.

### I faced `CParserError`. How can I extract multiple tables?

Use `mutiple_tables` option. Note: This option is experimental.
