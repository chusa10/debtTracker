# storage.py
import json
import os
import sys

FILENAME = "accounts_data.json"


def _get_data_path():
    """
    Return folder where accounts_data.json should live.
    - When running as .exe (PyInstaller), place it next to the .exe
    - When running from source, place it next to storage.py
    """
    if getattr(sys, "frozen", False):
        # running as bundled exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # running as normal python script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, FILENAME)


def load_accounts():
    path = _get_data_path()
    if not os.path.exists(path):
        # no file yet → return empty list, app will seed sample data
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_accounts(data):
    path = _get_data_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving accounts:", e)
