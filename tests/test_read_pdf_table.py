import unittest
import tabula
import tempfile
import filecmp
import json
import os
import pandas as pd
import shutil
import subprocess

# TODO: Remove this Python 2 compatibility code if possible
try:
    FileNotFoundError
    from unittest.mock import patch
except NameError:
    FileNotFoundError = IOError
    from mock import patch


class TestReadPdfTable(unittest.TestCase):
    def test_read_pdf(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        df = tabula.read_pdf(pdf_path)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(pd.read_csv(expected_csv1)))

    def test_read_remote_pdf(self):
        uri = "https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/12s0324.pdf"
        df = tabula.read_pdf(uri)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_read_pdf_into_json(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_json = 'tests/resources/data_1.json'
        json_data = tabula.read_pdf(pdf_path, output_format='json')
        self.assertTrue(isinstance(json_data, list))
        with open(expected_json) as json_file:
            data = json.load(json_file)
            self.assertEqual(json_data, data)

    def test_read_pdf_with_option(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        expected_csv2 = 'tests/resources/data_2-3.csv'
        expected_df2 = pd.read_csv(expected_csv2)
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1).equals(pd.read_csv(expected_csv1)))
        self.assertTrue(tabula.read_pdf(pdf_path, pages='2-3', stream=True).equals(expected_df2))
        self.assertTrue(tabula.read_pdf(pdf_path, pages=(2, 3), stream=True).equals(expected_df2))
        self.assertTrue(tabula.read_pdf(pdf_path, pages=(2, 3), stream=True,
                                        guess=True).equals(expected_df2))

    def test_read_pdf_file_like_obj(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        with open(pdf_path, 'rb') as f:
            df = tabula.read_pdf(f)
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue(df.equals(pd.read_csv(expected_csv1)))

    def test_read_pdf_pathlib(self):
        from pathlib import Path
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        df = tabula.read_pdf(Path(pdf_path))
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(pd.read_csv(expected_csv1)))

    def test_read_pdf_with_multiple_areas(self):
        # Original files are taken from https://github.com/tabulapdf/tabula-java/pull/213
        pdf_path = 'tests/resources/MultiColumn.pdf'
        expected_csv = 'tests/resources/MultiColumn.csv'
        expected_df = pd.read_csv(expected_csv)
        self.assertTrue(tabula.read_pdf(
            pdf_path, pages=1, area=[[0, 0, 100, 50], [0, 50, 100, 100]], relative_area=True).equals(expected_df))
        self.assertTrue(tabula.read_pdf(
            pdf_path, pages=1, area=[[0, 0, 451, 212], [0, 212, 451, 425]]).equals(expected_df))

    def test_read_pdf_with_java_option(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1, java_options=['-Xmx256m']
                                        ).equals(pd.read_csv(expected_csv1)))

    def test_read_pdf_with_pandas_option(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        column_name = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1, pandas_options={'header': None}
                                        ).equals(pd.read_csv(expected_csv1, header=None)))
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1, pandas_options={'header': 0}
                                        ).equals(pd.read_csv(expected_csv1, header=0)))
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1, pandas_options={'header': 'infer'}
                                        ).equals(pd.read_csv(expected_csv1, header='infer')))
        self.assertTrue(
            tabula.read_pdf(
                pdf_path, pages=1, pandas_options={'header': 'infer', 'names': column_name}
            ).equals(pd.read_csv(expected_csv1, header='infer', names=column_name))
        )
        self.assertTrue(
            tabula.read_pdf(
                pdf_path, pages=1, multiple_tables=True,
                pandas_options={'header': 'infer', 'names': column_name}
            )[0].equals(pd.read_csv(expected_csv1, header='infer', names=column_name))
        )
        self.assertTrue(
            tabula.read_pdf(
                pdf_path, pages=1, multiple_tables=True,
                pandas_options={'header': 'infer', 'columns': column_name}
            )[0].equals(pd.read_csv(expected_csv1, header='infer', names=column_name))
        )

    def test_read_pdf_for_multiple_tables(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'

        self.assertEqual(len(tabula.read_pdf(pdf_path, pages=2, multiple_tables=True)), 2)
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1, multiple_tables=True)[0].equals(
            pd.read_csv(expected_csv1, header=None)))
        with self.assertRaises(tabula.errors.CSVParseError):
            tabula.read_pdf(pdf_path, pages=2)

    def test_read_pdf_exception(self):
        invalid_pdf_path = 'notexist.pdf'
        with self.assertRaises(FileNotFoundError):
            tabula.read_pdf(invalid_pdf_path)

    def test_convert_from(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv = 'tests/resources/data_1.csv'
        expected_tsv = 'tests/resources/data_1.tsv'
        expected_json = 'tests/resources/data_1.json'
        temp = tempfile.NamedTemporaryFile()
        tabula.convert_into(pdf_path, temp.name, output_format='csv')
        self.assertTrue(filecmp.cmp(temp.name, expected_csv))
        tabula.convert_into(pdf_path, temp.name, output_format='tsv')
        self.assertTrue(filecmp.cmp(temp.name, expected_tsv))
        tabula.convert_into(pdf_path, temp.name, output_format='json')
        self.assertTrue(filecmp.cmp(temp.name, expected_json))

    def test_convert_into_by_batch(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv = 'tests/resources/data_1.csv'
        temp_dir = tempfile.mkdtemp()
        temp_pdf = temp_dir + '/data.pdf'
        converted_csv = temp_dir + '/data.csv'
        shutil.copyfile(pdf_path, temp_pdf)

        try:
            tabula.convert_into_by_batch(temp_dir, output_format='csv')
            self.assertTrue(filecmp.cmp(converted_csv, expected_csv))
        finally:
            shutil.rmtree(temp_dir)

    def test_convert_remote_file(self):
        uri = "https://github.com/tabulapdf/tabula-java/raw/master/src/test/resources/technology/tabula/12s0324.pdf"
        temp = tempfile.NamedTemporaryFile()
        tabula.convert_into(uri, temp.name, output_format='csv')
        self.assertTrue(os.path.exists(temp.name))

    def test_convert_into_exception(self):
        pdf_path = 'tests/resources/data.pdf'
        with self.assertRaises(AttributeError):
            tabula.convert_into(pdf_path, 'test.csv', output_format='dataframe')
        with self.assertRaises(AttributeError):
            tabula.convert_into(pdf_path, None)
        with self.assertRaises(AttributeError):
            tabula.convert_into(pdf_path, '')

    def test_read_pdf_with_template(self):
        pdf_path = 'tests/resources/data.pdf'
        template_path = 'tests/resources/data.tabula-template.json'
        expected_csv1 = 'tests/resources/data_1.csv'

        dfs = tabula.read_pdf_with_template(pdf_path, template_path)
        self.assertEqual(
            len(dfs),
            4)
        self.assertTrue(dfs[0].equals(
            pd.read_csv(expected_csv1)))

    @patch('subprocess.check_output')
    @patch('tabula.wrapper._jar_path')
    def test_read_pdf_with_jar_path(self, jar_func, mock_fun):
        jar_func.return_value = '/tmp/tabula-java.jar'
        pdf_path = 'tests/resources/data.pdf'

        tabula.read_pdf(pdf_path)
        mock_fun.assert_called_with(
            ['java', '-Dfile.encoding=UTF8', '-jar',
                '/tmp/tabula-java.jar', '--pages', '1', '--guess', 'tests/resources/data.pdf'])


if __name__ == '__main__':
    unittest.main()
