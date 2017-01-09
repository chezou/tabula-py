import unittest
import tabula
import pandas as pd

class TestReadPdfTable(unittest.TestCase):

    def test_read_pdf(self):
        pdf_path = 'tests/resources/data.pdf'
        self.assertTrue(isinstance(tabula.read_pdf_table(pdf_path), pd.DataFrame))

    def test_read_pdf_with_option(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_csv1 = 'tests/resources/data_1.csv'
        expected_csv2 = 'tests/resources/data_2-3.csv'
        self.assertTrue(tabula.read_pdf_table(pdf_path, pages=1).equals(pd.read_csv(expected_csv1)))
        self.assertTrue(tabula.read_pdf_table(pdf_path, pages='2-3', guess=False).equals(pd.read_csv(expected_csv2)))
        self.assertTrue(tabula.read_pdf_table(pdf_path, pages=(2, 3), guess=False).equals(pd.read_csv(expected_csv2)))

if __name__ == '__main__':
    unittest.main()