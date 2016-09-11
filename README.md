# tabula-py

`tabula-py` is a simple Python wrapper of [tabula-java](https://github.com/tabulapdf/tabula-java), which can read table of PDF.
You can read tables from PDF and convert into pandas's DataFrame.

![](http://i.imgur.com/ODM8hst.jpg)


# Requirements

- Java
- pandas

# Usage

## Install

```
pip install tabula-py
```

## Example

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
- spreadsheet (bool, optional):
  - Force PDF to be extracted using spreadsheet-style extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
- nospreadsheet (bool, optional):
  - Force PDF not to be extracted using spreadsheet-style extraction (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
- password (bool, optional):
  - Password to decrypt document. Default is empty
- silent (bool, optional):
  - Suppress all stderr output.

