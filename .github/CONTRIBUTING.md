# How to contribute

## Code formatting and testing

If you want to become a contributor, you can install dependency after cloning the repo as follows:


    git clone git@github.com:chezou/tabula-py.git
    pip install -e .[dev, test]
    pip install nox

For running tests and linter, run nox command.


    nox


## Documentation

You can build document on your environment as follows:


    pip install -e .[doc]
    cd docs && make html

The documentation source is under `docs/` directory and the document is published on Read the Docs automatically.

