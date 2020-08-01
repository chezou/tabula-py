import filecmp
import json
import os
import platform
import shutil
import subprocess
import tempfile
import unittest
import uuid
from unittest.mock import patch

import pandas as pd

import tabula


class TestReadPdfTable(unittest.TestCase):
    def setUp(self):
        self.uri = (
            "https://github.com/chezou/tabula-py/raw/"
            "master/tests/resources/12s0324.pdf"
        )
        self.pdf_path = "tests/resources/data.pdf"
        self.expected_csv1 = "tests/resources/data_1.csv"

    def test_read_pdf(self):
        df = tabula.read_pdf(self.pdf_path, stream=True)
        self.assertTrue(len(df), 1)
        self.assertTrue(isinstance(df[0], pd.DataFrame))
        self.assertTrue(df[0].equals(pd.read_csv(self.expected_csv1)))

    def test_read_remote_pdf(self):
        df = tabula.read_pdf(self.uri)
        self.assertTrue(len(df), 1)
        self.assertTrue(isinstance(df[0], pd.DataFrame))

    def test_read_remote_pdf_with_custom_user_agent(self):
        df = tabula.read_pdf(self.uri, user_agent="Mozilla/5.0", stream=True)
        self.assertTrue(len(df), 1)
        self.assertTrue(isinstance(df[0], pd.DataFrame))

    def test_read_pdf_into_json(self):
        expected_json = "tests/resources/data_1.json"
        json_data = tabula.read_pdf(
            self.pdf_path, output_format="json", stream=True, multiple_tables=False
        )
        self.assertTrue(isinstance(json_data, list))
        with open(expected_json) as json_file:
            data = json.load(json_file)
            self.assertEqual(json_data, data)

    def test_read_pdf_with_option(self):
        expected_csv2 = "tests/resources/data_2-3.csv"
        expected_df2 = pd.read_csv(expected_csv2)
        self.assertTrue(
            tabula.read_pdf(self.pdf_path, pages=1, stream=True)[0].equals(
                pd.read_csv(self.expected_csv1)
            )
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages="2-3",
                stream=True,
                guess=False,
                multiple_tables=False,
            )[0].equals(expected_df2)
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages=(2, 3),
                stream=True,
                guess=False,
                multiple_tables=False,
            )[0].equals(expected_df2)
        )

    def test_read_pdf_with_columns(self):
        pdf_path = "tests/resources/campaign_donors.pdf"
        expected_csv = "tests/resources/campaign_donors.csv"
        self.assertTrue(
            tabula.read_pdf(
                pdf_path, columns=[47, 147, 256, 310, 375, 431, 504], guess=False
            )[0].equals(pd.read_csv(expected_csv))
        )

    def test_read_pdf_file_like_obj(self):
        with open(self.pdf_path, "rb") as f:
            df = tabula.read_pdf(f, stream=True)
            self.assertTrue(len(df), 1)
            self.assertTrue(isinstance(df[0], pd.DataFrame))
            self.assertTrue(df[0].equals(pd.read_csv(self.expected_csv1)))

    def test_read_pdf_pathlib(self):
        from pathlib import Path

        df = tabula.read_pdf(Path(self.pdf_path), stream=True)
        self.assertTrue(len(df), 1)
        self.assertTrue(isinstance(df[0], pd.DataFrame))
        self.assertTrue(df[0].equals(pd.read_csv(self.expected_csv1)))

    def test_read_pdf_with_multiple_areas(self):
        # Original files are taken from
        # https://github.com/tabulapdf/tabula-java/pull/213
        pdf_path = "tests/resources/MultiColumn.pdf"
        expected_csv = "tests/resources/MultiColumn.csv"
        expected_df = pd.read_csv(expected_csv)
        self.assertTrue(
            tabula.read_pdf(
                pdf_path,
                pages=1,
                area=[[0, 0, 100, 50], [0, 50, 100, 100]],
                relative_area=True,
                multiple_tables=False,
            )[0].equals(expected_df)
        )
        self.assertTrue(
            tabula.read_pdf(
                pdf_path,
                pages=1,
                area=[[0, 0, 451, 212], [0, 212, 451, 425]],
                multiple_tables=False,
            )[0].equals(expected_df)
        )

    def test_read_pdf_with_java_option(self):
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, java_options=["-Xmx256m"]
            )[0].equals(pd.read_csv(self.expected_csv1))
        )

    def test_read_pdf_with_pandas_option(self):
        column_name = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": None}
            )[0].equals(pd.read_csv(self.expected_csv1, header=None))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": 0}
            )[0].equals(pd.read_csv(self.expected_csv1, header=0))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": "infer"}
            )[0].equals(pd.read_csv(self.expected_csv1, header="infer"))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages=1,
                stream=True,
                pandas_options={"header": "infer", "names": column_name},
            )[0].equals(
                pd.read_csv(self.expected_csv1, header="infer", names=column_name)
            )
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages=1,
                stream=True,
                multiple_tables=True,
                pandas_options={"header": "infer", "names": column_name},
            )[0].equals(
                pd.read_csv(self.expected_csv1, header="infer", names=column_name)
            )
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages=1,
                stream=True,
                multiple_tables=True,
                pandas_options={"header": "infer", "columns": column_name},
            )[0].equals(
                pd.read_csv(self.expected_csv1, header="infer", names=column_name)
            )
        )

    def test_read_pdf_for_multiple_tables(self):
        self.assertEqual(
            len(
                tabula.read_pdf(
                    self.pdf_path, pages=2, multiple_tables=True, stream=True
                )
            ),
            2,
        )
        self.assertTrue(
            tabula.read_pdf(self.pdf_path, pages=1, multiple_tables=True, stream=True)[
                0
            ].equals(pd.read_csv(self.expected_csv1))
        )
        with self.assertRaises(tabula.errors.CSVParseError):
            tabula.read_pdf(self.pdf_path, pages=2, multiple_tables=False)

    def test_read_pdf_exception(self):
        invalid_pdf_path = "notexist.pdf"
        with self.assertRaises(FileNotFoundError):
            tabula.read_pdf(invalid_pdf_path)
        with self.assertRaises(TypeError):
            tabula.read_pdf(self.pdf_path, unknown_option="foo")
        with self.assertRaises(ValueError):
            tabula.read_pdf(self.pdf_path, output_format="unknown")

    def test_convert_from(self):
        expected_tsv = "tests/resources/data_1.tsv"
        expected_json = "tests/resources/data_1.json"
        with tempfile.TemporaryDirectory() as tempdir:
            temp = os.path.join(tempdir, str(uuid.uuid4()))
            tabula.convert_into(self.pdf_path, temp, output_format="csv", stream=True)
            self.assertTrue(filecmp.cmp(temp, self.expected_csv1))
            tabula.convert_into(self.pdf_path, temp, output_format="tsv", stream=True)
            self.assertTrue(filecmp.cmp(temp, expected_tsv))
            tabula.convert_into(self.pdf_path, temp, output_format="json", stream=True)
            self.assertTrue(filecmp.cmp(temp, expected_json))

    def test_convert_into_by_batch(self):
        temp_dir = tempfile.mkdtemp()
        temp_pdf = temp_dir + "/data.pdf"
        converted_csv = temp_dir + "/data.csv"
        shutil.copyfile(self.pdf_path, temp_pdf)

        try:
            tabula.convert_into_by_batch(temp_dir, output_format="csv", stream=True)
            self.assertTrue(filecmp.cmp(converted_csv, self.expected_csv1))
        finally:
            shutil.rmtree(temp_dir)

        with self.assertRaises(ValueError):
            tabula.convert_into_by_batch(None, output_format="csv")

    def test_convert_remote_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            temp = os.path.join(tempdir, str(uuid.uuid4()))
            tabula.convert_into(self.uri, temp, output_format="csv")
            self.assertTrue(os.path.exists(temp))

    def test_convert_into_exception(self):
        with self.assertRaises(ValueError):
            tabula.convert_into(self.pdf_path, "test.csv", output_format="dataframe")
        with self.assertRaises(ValueError):
            tabula.convert_into(self.pdf_path, None)
        with self.assertRaises(ValueError):
            tabula.convert_into(self.pdf_path, "")

    def test_read_pdf_with_template(self):
        template_path = "tests/resources/data.tabula-template.json"

        dfs = tabula.read_pdf_with_template(self.pdf_path, template_path)
        self.assertEqual(len(dfs), 4)
        self.assertTrue(dfs[0].equals(pd.read_csv(self.expected_csv1)))

    def test_read_pdf_with_remote_template(self):
        template_path = (
            "https://github.com/chezou/tabula-py/raw/master/"
            "tests/resources/data.tabula-template.json"
        )

        dfs = tabula.read_pdf_with_template(self.pdf_path, template_path)
        self.assertEqual(len(dfs), 4)
        self.assertTrue(dfs[0].equals(pd.read_csv(self.expected_csv1)))

    @patch("subprocess.run")
    @patch("tabula.io._jar_path")
    def test_read_pdf_with_jar_path(self, jar_func, mock_fun):
        jar_func.return_value = "/tmp/tabula-java.jar"

        tabula.read_pdf(self.pdf_path, encoding="utf-8")

        target_args = ["java"]
        if platform.system() == "Darwin":
            target_args += ["-Djava.awt.headless=true"]
        target_args += [
            "-Dfile.encoding=UTF8",
            "-jar",
            "/tmp/tabula-java.jar",
            "--guess",
            "--format",
            "JSON",
            "tests/resources/data.pdf",
        ]
        subp_args = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "check": True,
        }
        mock_fun.assert_called_with(target_args, **subp_args)

    def test_read_pdf_with_dtype_string(self):
        pdf_path = "tests/resources/data_dtype.pdf"
        expected_csv = "tests/resources/data_dtype_expected.csv"
        expected_csv2 = "tests/resources/data_2-3.csv"
        template_path = "tests/resources/data_dtype.tabula-template.json"
        template_expected_csv = "tests/resources/data_dtype_template_expected.csv"

        pandas_options = {"dtype": str}
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                stream=True,
                pages=1,
                multiple_tables=False,
                pandas_options=pandas_options.copy(),
            )[0].equals(pd.read_csv(self.expected_csv1, **pandas_options))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages="2-3",
                stream=True,
                guess=False,
                multiple_tables=False,
                pandas_options=pandas_options.copy(),
            )[0].equals(pd.read_csv(expected_csv2, **pandas_options))
        )

        pandas_options = {"header": None, "dtype": str}
        dfs = tabula.read_pdf(
            pdf_path, multiple_tables=True, pandas_options=pandas_options.copy()
        )
        self.assertEqual(len(dfs), 4)
        self.assertTrue(dfs[0].equals(pd.read_csv(expected_csv, **pandas_options)))

        dfs_template = tabula.read_pdf_with_template(
            pdf_path,
            template_path,
            stream=True,
            pages="all",
            pandas_options=pandas_options.copy(),
        )
        self.assertEqual(len(dfs_template), 5)
        self.assertTrue(
            dfs_template[0].equals(pd.read_csv(template_expected_csv, **pandas_options))
        )

    @patch("subprocess.run")
    @patch("tabula.io._jar_path")
    def test_read_pdf_with_silent_false(self, jar_func, mock_fun):
        jar_func.return_value = "/tmp/tabula-java.jar"

        tabula.read_pdf(self.pdf_path, encoding="utf-8", silent=False)

        target_args = ["java"]
        if platform.system() == "Darwin":
            target_args += ["-Djava.awt.headless=true"]
        target_args += [
            "-Dfile.encoding=UTF8",
            "-jar",
            "/tmp/tabula-java.jar",
            "--guess",
            "--format",
            "JSON",
            "tests/resources/data.pdf",
        ]
        subp_args = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "check": True,
        }
        mock_fun.assert_called_with(target_args, **subp_args)

    @patch("subprocess.run")
    @patch("tabula.io._jar_path")
    def test_read_pdf_with_silent_true(self, jar_func, mock_fun):
        jar_func.return_value = "/tmp/tabula-java.jar"

        tabula.read_pdf(self.pdf_path, encoding="utf-8", silent=True)

        target_args = ["java"]
        if platform.system() == "Darwin":
            target_args += ["-Djava.awt.headless=true"]
        target_args += [
            "-Dfile.encoding=UTF8",
            "-Dorg.slf4j.simpleLogger.defaultLogLevel=off",
            "-Dorg.apache.commons.logging.Log=org.apache.commons.logging.impl.NoOpLog",
            "-jar",
            "/tmp/tabula-java.jar",
            "--guess",
            "--format",
            "JSON",
            "--silent",
            "tests/resources/data.pdf",
        ]
        subp_args = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "check": True,
        }
        mock_fun.assert_called_with(target_args, **subp_args)


if __name__ == "__main__":
    unittest.main()
