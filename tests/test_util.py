import unittest
import tabula


class TestUtil(unittest.TestCase):
    def test_environment_info(self):
        self.assertEqual(tabula.environment_info(), None)


if __name__ == '__main__':
    unittest.main()
