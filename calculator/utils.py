import os
import json
import csv
from typing import Callable, List

from calculator import models


async def insert_records_from_api(json_file_name: str, api_fetch: Callable, bulk_insert_data: Callable) -> List[models.ConnectedRealmsIndex]:
    print(f"Inserting data using {bulk_insert_data}...")
    json_file_path = create_json_path(json_file_name)

    json_data = load_data_from_cache(json_file_path)

    if json_data == None:
        json_data = await api_fetch()
        save_data_to_cache(json_file_path, json_data)
    print(f"Finished inserting data with {bulk_insert_data}!")
    return await bulk_insert_data(json_data)

async def insert_records_from_csv(csv_file_name: str, bulk_insert_data: Callable) -> List[models.ConnectedRealmsIndex]:
    print(f"Inserting data using {bulk_insert_data}...")
    csv_file_path = create_csv_path(csv_file_name)

    csv_data = load_data_from_cache(csv_file_path)
    print(f"Finished inserting data with {bulk_insert_data}!")

    return await bulk_insert_data(csv_data)

def insert_from_csv(csv_file_name: str, bulk_insert_data: Callable) -> List[models.ConnectedRealmsIndex]:
    print(f"Inserting data using {bulk_insert_data}...")
    csv_file_path = create_csv_path(csv_file_name)

    csv_data = load_data_from_cache(csv_file_path)
    inserted_records = bulk_insert_data(csv_data)
    print(f"Finished inserting data with {bulk_insert_data}!")

    return inserted_records

def create_csv_path(file_name: str):
    csv_folder = "wow_csv_data"
    return os.path.join(os.path.dirname(__file__), csv_folder, file_name)

def create_json_path(file_name: str):
    json_folder = "wow_json_data"    
    return os.path.join(os.path.dirname(__file__), json_folder, file_name)

def load_data_from_cache(file_path: str) -> dict | List[List]:
    if os.path.exists(file_path):
        with open(file_path, "r") as cache_file:
            try:
                return json.load(cache_file)
            except json.decoder.JSONDecodeError:
                cache_file.seek(0)
                read_csv = csv.reader(cache_file)
                next(cache_file)
                return list(read_csv)
    return None

def save_data_to_cache(file_path: str, data) -> None:
    with open(file_path, "w") as cache_file:
        json.dump(data, cache_file)

def convert_to_int_or_none(number: str):
    try:
        return int(number)
    except ValueError:
        return None

def convert_to_float_or_none(number: str):
    try:
        return float(number)
    except ValueError:
        return None     


# async def _if_json_file_doesnt_exist_create_one(json_file_path, get_data, *params):
#     if not os.path.exists(json_file_path):
#         if callable(get_data):
#             json_to_write = await get_data(*params)
#         else:
#             json_to_write = get_data
#         await _write_json_to_file(json_file_path, json_to_write)

# async def _write_json_to_file(path, json_to_write):
#     serialized_json = json.dumps(json_to_write)

#     with open(path, "w") as json_file:
#         json_file.write(serialized_json)

# def get_data_from_csv(csv_path: str, data_extration_func: Callable):
#     with open(csv_path, "r", encoding='utf-8-sig') as file:
#         opened_csv = csv.reader(file)
#         next(opened_csv)
#         return data_extration_func(opened_csv)