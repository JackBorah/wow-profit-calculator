from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from calculator.utils import *

class TestCreatePaths(TestCase):
    def test_get_csv_path(self):
        actual_path = create_csv_path("test.csv")
        expected_path = r"C:\Users\Jack\Projects\wowprofitcalculator\calculator\wow_csv_data\test.csv"

        self.assertEqual(expected_path, actual_path)

    def test_get_json_path(self):
        actual_path = create_json_path("test.json")
        expected_path = r"C:\Users\Jack\Projects\wowprofitcalculator\calculator\wow_json_data\test.json"

        self.assertEqual(expected_path, actual_path)

class TestCacheFunctionsWithJson(TestCase):
    test_file_name = "test_cache.json"
    test_file_path = create_json_path(test_file_name)
    test_data = {"key": "value"}
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_load_json_data_from_cache(self):
        with open(self.test_file_path, "w") as test_file:
            json.dump(self.test_data, test_file)
                      
        result = load_data_from_cache(self.test_file_path)

        self.assertIsNotNone(result)
        self.assertEqual(result, self.test_data)

    def test_load_data_from_non_existing_cache(self):
        non_existing_file_path = "non_existing_cache.json"

        result = load_data_from_cache(non_existing_file_path)
        self.assertIsNone(result)

    def test_save_data_to_cache_success(self):
        save_data_to_cache(self.test_file_path, self.test_data)

        # Check if the file was created
        self.assertTrue(os.path.exists(self.test_file_path))

        # Check if the saved data is correct
        loaded_data = load_data_from_cache(self.test_file_path)
        self.assertEqual(loaded_data, self.test_data)

class TestCacheFunctionsWithCsv(TestCase):
    test_file_name = "test_cache.csv"
    test_file_path = create_csv_path(test_file_name)
    test_data = [["column1","column2"],["test","data"]]

    def tearDown(self) -> None:
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_load_csv_data_from_cache(self):
        with open(self.test_file_path, 'w', newline='') as test_file:
            test_data_writer = csv.writer(test_file)
            test_data_writer.writerows(self.test_data)
                      
        result = load_data_from_cache(self.test_file_path)
        expected_data = [["test","data"]]

        self.assertIsNotNone(result)
        self.assertEqual(expected_data, result)

    def test_save_data_to_cache_success(self):
        save_data_to_cache(self.test_file_path, self.test_data)

        # Check if the file was created
        self.assertTrue(os.path.exists(self.test_file_path))

        # Check if the saved data is correct
        loaded_data = load_data_from_cache(self.test_file_path)

        self.assertEqual(loaded_data, self.test_data)


class TestPathsAndCacheFunctionsIntegrate(TestCase):
    test_json_file_name = "test_cache.json"
    test_csv_file_name = "test_cache.csv"
    test_json_file_path = create_json_path(test_json_file_name)
    test_csv_file_path = create_csv_path(test_csv_file_name)
    test_json_data = {"key": "value"}
    test_csv_data = "test,data"

    def tearDown(self) -> None:
        if os.path.exists(self.test_json_file_path):
            os.remove(self.test_json_file_path)
        if os.path.exists(self.test_csv_file_path):
            os.remove(self.test_csv_file_path)

    def test_create_json_path_and_save_data_to_cache_work_together(self):
        save_data_to_cache(self.test_json_file_path, self.test_json_data)

        saved_data = load_data_from_cache(self.test_json_file_path)
        self.assertEqual(saved_data, self.test_json_data)

    def test_create_csv_path_and_save_data_to_cache_work_together(self):
        save_data_to_cache(self.test_csv_file_path, self.test_csv_data)

        saved_data = load_data_from_cache(self.test_csv_file_path)
        self.assertEqual(saved_data, self.test_csv_data)


class TestInsertRecordsFromApi(IsolatedAsyncioTestCase):
    json_file_name = "test_data.json"
    json_file_path = create_json_path(json_file_name)
    test_data = {"data": [1, 2, 3]}

    async def asyncTearDown(self):
        if os.path.exists(self.json_file_path):
            os.remove(self.json_file_path)

    async def test_insert_records_from_api_data_loaded_from_cache(self):
        json_file_path = create_json_path(self.json_file_name)

        save_data_to_cache(json_file_path, self.test_data)

        api_fetch_mock = AsyncMock()
        bulk_insert_data_mock = AsyncMock(return_value=[1,2,3])

        inserted_records = await insert_records_from_api(
            self.json_file_name,
            api_fetch_mock,
            bulk_insert_data_mock,
        )

        api_fetch_mock.assert_not_awaited()
        self.assertEqual(self.test_data["data"], inserted_records)

    async def test_insert_records_from_api_data_not_in_cache(self):
        api_fetch_mock = AsyncMock(return_value=self.test_data)
        bulk_insert_data_mock = AsyncMock(return_value=[1,2,3])

        inserted_records = await insert_records_from_api(
            self.json_file_name,
            api_fetch_mock,
            bulk_insert_data_mock,
        )

        self.assertEqual(self.test_data["data"], inserted_records)


class TestInsertRecordsFromCsv(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.csv_file_name = "test_data.csv"
        self.csv_file_path = create_json_path(self.csv_file_name)
        self.test_data = "1,2,3\n4,5,6"

        save_data_to_cache(self.csv_file_path, self.test_data)

    async def asyncTearDown(self):
        if os.path.exists(self.csv_file_path):
            os.remove(self.csv_file_path)

    async def test_insert_records_from_csv_success(self):
        bulk_insert_data_mock = AsyncMock(return_value=2)

        records_count = await insert_records_from_csv(
            self.csv_file_name,
            bulk_insert_data_mock,
        )

        self.assertEqual(records_count, 2)