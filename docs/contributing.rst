Contributing to tabula-py
=========================

Interested in helping out? I'd love to have your help!

You can help by:


* `Reporting a bug <https://github.com/chezou/tabula-py/issues>`_.
* Adding or editing documentation.
* Contributing code via a Pull Request.
* Write a blog post or spreading the word about ``tabula-py`` to people who might be able to benefit from using it.


Code formatting and testing
---------------------------

If you want to become a contributor, you can install dependency after cloning the repo as follows:

.. code-block:: bash

   pip install -e .[dev, test]
   pip install nox

For running tests and linter, run nox command.

.. code-block:: bash

   nox .


Documentation
-------------

You can build document on your environment as follows:

.. code-block:: bash

   pip install -e .[doc]
   cd docs && make html

The documentation source is under ``docs/`` directory and the document is published on Read the Docs automatically.
