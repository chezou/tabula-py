import unittest
from unittest.mock import MagicMock, patch

import tabula


class TestUtil(unittest.TestCase):
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

        tabula.file_util.localize_file(uri, user_agent=user_agent)
        mock_fun.assert_called_with(uri, user_agent)


if __name__ == "__main__":
    unittest.main()
