import filecmp
import json
import os
import platform
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import tabula


class TestReadPdfTable(unittest.TestCase):
    def setUp(self):
        self.uri = (
            "https://github.com/tabulapdf/tabula-java/raw/"
            "master/src/test/resources/technology/tabula/12s0324.pdf"
        )
        self.pdf_path = "tests/resources/data.pdf"
        self.expected_csv1 = "tests/resources/data_1.csv"

    def test_read_pdf(self):
        df = tabula.read_pdf(self.pdf_path, stream=True)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(pd.read_csv(self.expected_csv1)))

    def test_read_remote_pdf(self):
        df = tabula.read_pdf(self.uri)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_read_remote_pdf_with_custom_user_agent(self):
        df = tabula.read_pdf(self.uri, user_agent="Mozilla/5.0", stream=True)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_read_pdf_into_json(self):
        expected_json = "tests/resources/data_1.json"
        json_data = tabula.read_pdf(self.pdf_path, output_format="json", stream=True)
        self.assertTrue(isinstance(json_data, list))
        with open(expected_json) as json_file:
            data = json.load(json_file)
            self.assertEqual(json_data, data)

    def test_read_pdf_with_option(self):
        expected_csv2 = "tests/resources/data_2-3.csv"
        expected_df2 = pd.read_csv(expected_csv2)
        self.assertTrue(
            tabula.read_pdf(self.pdf_path, pages=1, stream=True).equals(
                pd.read_csv(self.expected_csv1)
            )
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages="2-3", stream=True, guess=False
            ).equals(expected_df2)
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=(2, 3), stream=True, guess=False
            ).equals(expected_df2)
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=(2, 3), stream=True, guess=False
            ).equals(expected_df2)
        )

    def test_read_pdf_file_like_obj(self):
        with open(self.pdf_path, "rb") as f:
            df = tabula.read_pdf(f, stream=True)
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue(df.equals(pd.read_csv(self.expected_csv1)))

    def test_read_pdf_pathlib(self):
        from pathlib import Path

        df = tabula.read_pdf(Path(self.pdf_path), stream=True)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(pd.read_csv(self.expected_csv1)))

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
            ).equals(expected_df)
        )
        self.assertTrue(
            tabula.read_pdf(
                pdf_path, pages=1, area=[[0, 0, 451, 212], [0, 212, 451, 425]]
            ).equals(expected_df)
        )

    def test_read_pdf_with_java_option(self):
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, java_options=["-Xmx256m"]
            ).equals(pd.read_csv(self.expected_csv1))
        )

    def test_read_pdf_with_pandas_option(self):
        column_name = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": None}
            ).equals(pd.read_csv(self.expected_csv1, header=None))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": 0}
            ).equals(pd.read_csv(self.expected_csv1, header=0))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path, pages=1, stream=True, pandas_options={"header": "infer"}
            ).equals(pd.read_csv(self.expected_csv1, header="infer"))
        )
        self.assertTrue(
            tabula.read_pdf(
                self.pdf_path,
                pages=1,
                stream=True,
                pandas_options={"header": "infer", "names": column_name},
            ).equals(pd.read_csv(self.expected_csv1, header="infer", names=column_name))
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
            ].equals(pd.read_csv(self.expected_csv1, header=None))
        )
        with self.assertRaises(tabula.errors.CSVParseError):
            tabula.read_pdf(self.pdf_path, pages=2)

    def test_read_pdf_exception(self):
        invalid_pdf_path = "notexist.pdf"
        with self.assertRaises(FileNotFoundError):
            tabula.read_pdf(invalid_pdf_path)

    def test_convert_from(self):
        expected_tsv = "tests/resources/data_1.tsv"
        expected_json = "tests/resources/data_1.json"
        temp = tempfile.NamedTemporaryFile()
        tabula.convert_into(self.pdf_path, temp.name, output_format="csv", stream=True)
        self.assertTrue(filecmp.cmp(temp.name, self.expected_csv1))
        tabula.convert_into(self.pdf_path, temp.name, output_format="tsv", stream=True)
        self.assertTrue(filecmp.cmp(temp.name, expected_tsv))
        tabula.convert_into(self.pdf_path, temp.name, output_format="json", stream=True)
        self.assertTrue(filecmp.cmp(temp.name, expected_json))

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

    def test_convert_remote_file(self):
        temp = tempfile.NamedTemporaryFile()
        tabula.convert_into(self.uri, temp.name, output_format="csv")
        self.assertTrue(os.path.exists(temp.name))

    def test_convert_into_exception(self):
        with self.assertRaises(AttributeError):
            tabula.convert_into(self.pdf_path, "test.csv", output_format="dataframe")
        with self.assertRaises(AttributeError):
            tabula.convert_into(self.pdf_path, None)
        with self.assertRaises(AttributeError):
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
    @patch("tabula.wrapper._jar_path")
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
            "--pages",
            "1",
            "--guess",
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
