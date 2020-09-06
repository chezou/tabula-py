import os
import unittest
from unittest.mock import MagicMock, patch

import tabula


class TestUtil(unittest.TestCase):
    def setUp(self):
        tabula.file_util.MAX_FILE_SIZE = 30

    def test_environment_info(self):
        self.assertEqual(tabula.environment_info(), None)

    @patch("tabula.file_util.shutil.copyfileobj")
    @patch("tabula.file_util.urlopen")
    @patch("tabula.file_util._create_request")
    def test_localize_file_with_user_agent(
        self, mock_fun, mock_urlopen, mock_copyfileobj
    ):
        uri = (
            "https://github.com/tabulapdf/tabula-java/raw/"
            "master/src/test/resources/technology/tabula/12s0324.pdf"
        )
        user_agent = "Mozilla/5.0"

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = b"contents"
        cm.geturl.return_value = uri
        mock_urlopen.return_value = cm

        fname, _ = tabula.file_util.localize_file(uri, user_agent=user_agent)
        mock_fun.assert_called_with(uri, user_agent)
        self.addCleanup(os.remove, fname)

    @patch("tabula.file_util.shutil.copyfileobj")
    @patch("tabula.file_util.urlopen")
    def test_localize_file_with_non_ascii_url(self, mock_urlopen, mock_copyfileobj):
        uri = (
            "https://github.com/tabulapdf/tabula-java/raw/"
            "master/src/test/resources/technology/tabula/日本語.pdf"
        )
        expected_uri = (
            "https://github.com/tabulapdf/tabula-java/raw/master/src/test/"
            "resources/technology/tabula/%E6%97%A5%E6%9C%AC%E8%AA%9E.pdf"
        )

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = b"contents"
        cm.geturl.return_value = uri
        mock_urlopen.return_value = cm

        fname, _ = tabula.file_util.localize_file(uri)
        mock_urlopen.assert_called_with(expected_uri)
        self.addCleanup(os.remove, fname)

    @patch("tabula.file_util.shutil.copyfileobj")
    @patch("tabula.file_util.urlopen")
    def test_localize_file_with_long_url(self, mock_urlopen, mock_copyfileobj):
        uri = (
            "https://github.com/tabulapdf/tabula-py/raw/"
            "master/src/tests/resources/"
            "12345678901234567890123456789012345.pdf"
        )

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = b"contents"
        cm.geturl.return_value = uri
        mock_urlopen.return_value = cm

        fname, _ = tabula.file_util.localize_file(uri)
        mock_urlopen.assert_called_with(uri)
        self.assertTrue(fname.endswith("123456789012345678901234567890.pdf"))
        self.addCleanup(os.remove, fname)


if __name__ == "__main__":
    unittest.main()
