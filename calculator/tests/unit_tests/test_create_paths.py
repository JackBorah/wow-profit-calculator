from unittest import TestCase
from unittest.mock import patch

from calculator.create_paths import create_csv_path, create_json_path

@patch("calculator.create_paths._base_url", ".")
class TestCreatePaths(TestCase):
    def test_get_csv_path(self):
        actual_path = create_csv_path("test.csv")
        expected_path = r".\wow_csv_data\test.csv"

        self.assertEqual(expected_path, actual_path)

    def test_get_json_path(self):
        actual_path = create_json_path("test.json")
        expected_path = r".\wow_json_data\test.json"

        self.assertEqual(expected_path, actual_path)
