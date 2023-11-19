import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

import jpype
import pytest

import tabula


class TestReadPdfJarPath(unittest.TestCase):
    def setUp(self):
        self.pdf_path = "tests/resources/data.pdf"

    @patch("tabula.backend.jar_path")
    def test_read_pdf_with_jar_path(self, jar_func):
        jar_func.return_value = "/tmp/tabula-java.jar"

        # Fallback to subprocess
        with pytest.raises(CalledProcessError):
            tabula.read_pdf(self.pdf_path, encoding="utf-8")
        file_name = Path(jpype.getClassPath()).name
        self.assertEqual(file_name, "tabula-java.jar")
