import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

import tabula


class TestReadPdfJarPath(unittest.TestCase):
    def setUp(self):
        self.pdf_path = "tests/resources/data.pdf"

    @patch("tabula.io.TabulaVm._jar_path")
    def test_read_pdf_with_jar_path(self, jar_func):
        jar_func.return_value = "/tmp/tabula-java.jar"

        with pytest.raises(ImportError):
            tabula.read_pdf(self.pdf_path, encoding="utf-8")
        file_name = Path(tabula.io.jpype.getClassPath()).name
        self.assertEqual(file_name, "tabula-java.jar")
