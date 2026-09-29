import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("user_data.json")


def read_json():
    if not DATA_FILE.exists():
        return {}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(data):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
