Getting Started
================

Requirements
-------------


* Java

  * Java 8+

* Python

  * 3.7+


Installation
------------

Before installing tabula-py, ensure you have Java runtime on your environment.

You can install tabula-py form PyPI with ``pip`` command.

.. code-block:: bash

   pip install tabula-py


.. Note::
    conda recipe on conda-forge is not maintained by us.
    We recommend to install via ``pip`` to use latest version of tabula-py.

Get tabula-py working (Windows 10)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This instruction is originally written by `@lahoffm <https://github.com/lahoffm>`_. Thanks!


* If you don't have it already, install `Java <https://www.java.com/en/download/manual.jsp>`_
* Try to run example code (replace the appropriate PDF file name).
* If there's a ``FileNotFoundError`` when it calls ``read_pdf()``\ , and when you type ``java`` on command line it says
  ``'java' is not recognized as an internal or external command, operable program or batch file``\ , you should set ``PATH`` environment variable to point to the Java directory.
* Find the main Java folder like ``jre...`` or ``jdk...``. On Windows 10 it was under ``C:\Program Files\Java``
* On Windows 10: **Control Panel** -> **System and Security** -> **System** -> **Advanced System Settings** -> **Environment Variables** -> Select **PATH** --> **Edit**
* Add the ``bin`` folder like ``C:\Program Files\Java\jre1.8.0_144\bin``\ , hit OK a bunch of times.
* On command line, ``java`` should now print a list of options, and ``tabula.read_pdf()`` should run.


Example
-------

tabula-py enables you to extract tables from a PDF into a DataFrame, or a JSON. It can also extract tables from a PDF and save the file as a CSV, a TSV, or a JSON.

.. code-block:: py

   import tabula

   # Read pdf into a list of DataFrame
   dfs = tabula.read_pdf("test.pdf", pages='all')

   # Read remote pdf into a list of DataFrame
   dfs2 = tabula.read_pdf("https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/arabic.pdf")

   # convert PDF into CSV
   tabula.convert_into("test.pdf", "output.csv", output_format="csv", pages='all')

   # convert all PDFs in a directory
   tabula.convert_into_by_batch("input_directory", output_format='csv', pages='all')

See `example notebook <https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb>`_ for more detail. I also recommend to read `the tutorial article <https://aegis4048.github.io/parse-pdf-files-while-retaining-structure-with-tabula-py>`_ written by `@aegis4048 <https://github.com/aegis4048>`_.


.. Note::

   If you face some issue, we'd recommend to try `tabula.app <https://tabula.technology>`_ to see the limitation of tabula-java.
   Also, see :ref:`faq` as well.
