from pathlib import Path
from shutil import rmtree
from os import chmod, path, walk


files_exeptions = set()


def checkFileExistsAndDelete(filepath, skip_prompts):
    if filepath in files_exeptions:
        return
    file = Path(filepath)
    if file.exists() and (skip_prompts or input(f"The file {filepath} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
        try:
            if file.is_file():
                chmod(filepath, 0o777)
                print(f" ==> Removing file {filepath}")
                file.unlink()
            else:
                for root, dirs, files in walk(filepath):
                    for d in dirs:
                        chmod(path.join(root, d), 0o777)
                    for file in files:
                        chmod(path.join(root, file), 0o777)
                rmtree(filepath)
                print(f" ==> Removing directory {filepath}")
        except PermissionError:
            print(f"Unable to remove file {filepath} : Permission Error")
