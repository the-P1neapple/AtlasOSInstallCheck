import pathlib
from shutil import rmtree


def checkFileExistsAndDelete(filepath):
    file = pathlib.Path(filepath)
    if file.exists() and input(f"The file {filepath} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y':
        try:
            if file.is_file():
                file.unlink()
            else:
                rmtree(filepath)
        except PermissionError:
            print(f"Unable to remove file {filepath} : Permission Error")
