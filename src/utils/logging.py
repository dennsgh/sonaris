import json
from pathlib import Path


def load_json_with_backup(path: Path):
    """
    Attempts to load a JSON file from the given path. If the file is corrupt,
    it creates a numbered backup and returns an empty dictionary.
    """
    if path.exists():
        try:
            with open(path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Corrupt JSON file detected: {e}. Creating a numbered backup.")
            backup_path = create_numbered_backup(path)
            path.rename(backup_path)
        except Exception as e:
            print(f"Unexpected error loading JSON file: {e}.")
    return {}


def save_json(data, path: Path):
    """
    Saves the given data as a JSON file to the specified path.
    """
    try:
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Unexpected error loading JSON file: {e}.")
        
def create_numbered_backup(original_path: Path):
    """
    Creates a numbered backup for the given path, ensuring no existing backup is overwritten.
    """
    backup_base = original_path.with_suffix(".bak")
    counter = 1
    new_backup = Path(f"{backup_base}_{counter}")
    while new_backup.exists():
        counter += 1
        new_backup = Path(f"{backup_base}_{counter}")
    return new_backup
