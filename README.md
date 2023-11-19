# tabula-py

[![Build Status](https://github.com/chezou/tabula-py/actions/workflows/pythontest.yml/badge.svg)](https://github.com/chezou/tabula-py/actions/workflows/pythontest.yml)
[![PyPI version](https://badge.fury.io/py/tabula-py.svg)](https://badge.fury.io/py/tabula-py)
[![Documentation Status](https://readthedocs.org/projects/tabula-py/badge/?version=latest)](https://tabula-py.readthedocs.io/en/latest/?badge=latest)
[![Patreon](https://img.shields.io/badge/patreon-donate-orange.svg)](https://www.patreon.com/chezou)

`tabula-py` is a simple Python wrapper of [tabula-java](https://github.com/tabulapdf/tabula-java), which can read tables in a PDF.
You can read tables from a PDF and convert them into a pandas DataFrame. tabula-py also enables you to convert a PDF file into a CSV, a TSV or a JSON file.

You can see [the example notebook](https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb) and try it on Google Colab, or we highly recommend reading [our documentation](https://tabula-py.readthedocs.io/en/latest/), especially the FAQ section.

![tabula-py example](https://github.com/chezou/tabula-py/raw/master/example.png)

## Requirements

- Java 8+
- Python 3.8+

### OS

I confirmed working on macOS and Ubuntu. But some people confirm it works on Windows 10. See also [the documentation for the detailed installation for Windows 10](https://tabula-py.readthedocs.io/en/latest/getting_started.html#get-tabula-py-working-windows-10).

## Usage

- [Documentation](https://tabula-py.readthedocs.io/en/latest/)
  - [FAQ](https://tabula-py.readthedocs.io/en/latest/faq.html) would be helpful if you have an issue
- [Example notebook on Google Colaboratory](https://colab.research.google.com/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb)

### Install

Ensure you have a Java runtime and set the PATH for it.

```bash
pip install tabula-py
```

If you want to leverage faster execution with jpype, install with `jpype` extra.

```sh
pip install tabula-py[jpype]
```

### Example

tabula-py enables you to extract tables from a PDF into a DataFrame, or a JSON. It can also extract tables from a PDF and save the file as a CSV, a TSV, or a JSON.  

```py
import tabula

# Read pdf into list of DataFrame
dfs = tabula.read_pdf("test.pdf", pages='all')

# Read remote pdf into list of DataFrame
dfs2 = tabula.read_pdf("https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/arabic.pdf")

# convert PDF into CSV file
tabula.convert_into("test.pdf", "output.csv", output_format="csv", pages='all')

# convert all PDFs in a directory
tabula.convert_into_by_batch("input_directory", output_format='csv', pages='all')
```

See [an example notebook](https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb) for more details. I also recommend reading [the tutorial article](https://aegis4048.github.io/parse-pdf-files-while-retaining-structure-with-tabula-py) written by [@aegis4048](https://github.com/aegis4048), and [another tutorial](https://www.dunderdata.com/blog/read-trapped-tables-within-pdfs-as-pandas-dataframes) written by [@tdpetrou](https://github.com/tdpetrou).

### Contributing

Interested in helping out? I'd love to have your help!

You can help by:

- [Reporting a bug](https://github.com/chezou/tabula-py/issues).
- Adding or editing documentation.
- Contributing code via a Pull Request. See also [for the contribution](docs/contributing.rst)
- Write a blog post or spread the word about `tabula-py` to people who might be able to benefit from using it.

#### Contributors

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
- [@red-bin](https://github.com/red-bin)
- [@alexandreio](https://github.com/alexandreio)
- [@bpben](https://github.com/bpben)
- [@Bueddl](https://github.com/Bueddl)
- [@cjotade](https://github.com/cjotade)
- [@codeboy5](https://github.com/codeboy5)
- [@manohar-voggu](https://github.com/manohar-voggu)
- [@deveshSingh06](https://github.com/deveshSingh06)
- [@grfeller](https://github.com/grfeller)
- [@djbrown](https://github.com/djbrown)
- [@swar](https://github.com/swar)
- [@mvoggu](https://github.com/mvoggu)
- [@tdpetrou](https://github.com/tdpetrou)

#### Another support

You can also support our continued work on `tabula-py` with a donation on GitHub Sponsors or [Patreon](https://www.patreon.com/chezou).
