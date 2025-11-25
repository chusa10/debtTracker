# storage.py
import json
import os
import sys

APP_NAME = "CreditTracker"
FILENAME = "accounts_data.json"


def _get_appdata_path():
    """
    Returns the AppData/Roaming/CreditTracker folder on Windows,
    or ~/.CreditTracker on other OS.
    """
    if sys.platform.startswith("win"):
        base_dir = os.getenv("APPDATA")  # C:\Users\<you>\AppData\Roaming
        app_dir = os.path.join(base_dir, APP_NAME)
    else:
        # macOS / Linux
        home = os.path.expanduser("~")
        app_dir = os.path.join(home, f".{APP_NAME}")

    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, FILENAME)


def load_accounts():
    path = _get_appdata_path()

    if not os.path.exists(path):
        # If no file, return empty list (app will seed defaults)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_accounts(data):
    path = _get_appdata_path()

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving accounts:", e)
