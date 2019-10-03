.. _faq:

FAQ
---

``tabula-py`` does not work
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several possible reasons, but ``tabula-py`` is just a wrapper of `tabula-java <https://github.com/tabulapdf/tabula-java>`_ , make sure you've installed Java and you can use ``java`` command on your terminal. Many issue reporters forget to set PATH for ``java`` command.

You can check whether tabula-py can call ``java`` from Python process with ``tabula.environment_info()`` function.

I can't ``from tabula import read_pdf``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you've installed ``tabula``\ , it will be conflict the namespace. You should install ``tabula-py`` after removing ``tabula``.

.. code-block:: bash

   pip uninstall tabula
   pip install tabula-py

The result is different from ``tabula-java``. Or, ``stream`` option seems not to work appropreately
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``tabula-py`` set ``guess`` option ``True`` by default, for beginners. It is known to make a conflict between ``stream`` option. If you feel something strange with your result, please set ``guess=False``.

Can I use option ``xxx``\ ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. You can use ``options`` argument as following. The format is same as cli of tabula-java.

.. code-block:: python

   read_pdf(file_path, options="--columns 10.1,20.2,30.3")

How can I ignore useless area?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In short, you can extract with ``area`` and ``spreadsheet`` option.

.. code-block:: python

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

How to use ``area`` option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

According to tabula-java wiki, there is a explain how to specify the area:
https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want

For example, using macOS's preview, I got area information of this `PDF <https://github.com/chezou/tabula-py/files/711877/table.pdf>`_\ :


.. image:: https://cloud.githubusercontent.com/assets/916653/22047470/b201de24-dd6a-11e6-9cfc-7bc73e33e3b2.png
   :target: https://cloud.githubusercontent.com/assets/916653/22047470/b201de24-dd6a-11e6-9cfc-7bc73e33e3b2.png
   :alt: image


.. code-block:: bash

   java -jar ./target/tabula-1.0.1-jar-with-dependencies.jar -p all -a $y1,$x1,$y2,$x2 -o $csvfile $filename

given

.. code-block:: python

   # Note the left, top, height, and width parameters and calculate the following:

   y1 = top
   x1 = left
   y2 = top + height
   x2 = left + width

I confirmed with tabula-java:

.. code-block:: bash

   java -jar ./tabula/tabula-1.0.1-jar-with-dependencies.jar -a "337.29,226.49,472.85,384.91" table.pdf

Without ``-r``\ (same as ``--spreadsheet``\ ) option, it does not work properly.

I faced ``ParserError: Error tokenizing data. C error``. How can I extract multiple tables?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This error occurs pandas trys to extract multiple tables with different column size at once.
Use ``multiple_tables`` option, then you can avoid this error.

I want to prevent tabula-py from stealing focus on every call on my mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set ``java_options=["-Djava.awt.headless=true"]``. kudos `@jakekara <https://twitter.com/jakekara/status/979031539697831937>`_

I got ``?`` character with result on Windows. How can I avoid it?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the encoding of PDF is UTF-8, you should set ``chcp 65001`` on your terminal before launching a Python process.

.. code-block:: sh

   chcp 65001

Then you can extract UTF-8 PDF with ``java_options="-Dfile.encoding=UTF8"`` option. This option will be added with ``encoding='utf-8'`` option, which is also set by default.

.. code-block:: python

   # This is an example for java_options is set explicitly
   df = read_pdf(file_path, java_options="-Dfile.encoding=UTF8")

Replace ``65001`` and ``UTF-8`` appropriately, if the file encoding isn't UTF-8.

I can't extract file/directory name with space on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You should escape file/directory name yourself.

I want to use a different tabula .jar  file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can specify the jar location via enviroment variable

.. code-block:: bash

   export TABULA_JAR=".../tabula-x.y.z-jar-with-dependencies.jar"

I want to extract multiple tables from a document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use the following example code

.. code-block:: python

   df = read_pdf(file_path, multiple_tables=True)

The result will be a list of DataFrames.  If you want separate tables across all pages in a document, use the ``pages`` argument.

Table cell contents sometimes overflow into the next row.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can try using ``lattice=True``\ , which will often work if there are lines separating cells in the table.
