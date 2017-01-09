import unittest
import tabula
import tempfile
import filecmp
import json
import pandas as pd


class TestReadPdfTable(unittest.TestCase):

    def test_read_pdf(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        df = tabula.read_pdf(pdf_path)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(pd.read_csv(expected_csv1)))

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
        self.assertTrue(tabula.read_pdf(pdf_path, pages=1).equals(pd.read_csv(expected_csv1)))
        self.assertTrue(tabula.read_pdf(pdf_path, pages='2-3', guess=False).equals(pd.read_csv(expected_csv2)))
        self.assertTrue(tabula.read_pdf(pdf_path, pages=(2, 3), guess=False).equals(pd.read_csv(expected_csv2)))

    def test_conver_from(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv = 'tests/resources/data_1.csv'
        expected_tsv = 'tests/resources/data_1.tsv'
        expected_json = 'tests/resources/data_1.json'
        temp = tempfile.NamedTemporaryFile()
        tabula.convert_from(pdf_path, temp.name, output_format='csv')
        self.assertTrue(filecmp.cmp(temp.name, expected_csv))
        tabula.convert_from(pdf_path, temp.name, output_format='tsv')
        self.assertTrue(filecmp.cmp(temp.name, expected_tsv))
        tabula.convert_from(pdf_path, temp.name, output_format='json')
        self.assertTrue(filecmp.cmp(temp.name, expected_json))


if __name__ == '__main__':
    unittest.main()
