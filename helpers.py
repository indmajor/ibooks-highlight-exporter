import getpass
import os


def get_username() -> str:
    return getpass.getuser()


def find_first_file_with_extension(directory_path: str, extension: str) -> str:
    for file in os.listdir(directory_path):
        if file.endswith(f".{extension}"):
            return os.path.join(directory_path, file)


def get_database_path(db_directory_path: str) -> str:
    return find_first_file_with_extension(db_directory_path, "sqlite")


def get_ibooks_assets_database_path() -> str:
    username = get_username()
    db_directory_path = f"/Users/{username}/Library/Containers/com.apple.iBooksX/Data/Documents/BKLibrary"
    return get_database_path(db_directory_path)


def get_ibooks_annotations_database_path() -> str:
    username = get_username()
    db_directory_path = f"/Users/{username}/Library/Containers/com.apple.iBooksX/Data/Documents/AEAnnotation"
    return get_database_path(db_directory_path)
