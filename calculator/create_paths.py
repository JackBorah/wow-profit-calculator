import os

_base_url = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\\"

def create_csv_path(file_name: str):
    csv_folder = r"wow_csv_data"
    return os.path.join(_base_url, csv_folder, file_name)

def create_json_path(file_name: str):
    json_folder = r"wow_json_data"    
    return os.path.join(_base_url, json_folder, file_name)
