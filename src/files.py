from pathlib import Path
from shutil import rmtree
import os

def checkFileExistsAndDelete(filepath, skip_prompts):
    file = Path(filepath)
    if file.exists() and (skip_prompts or input(f"The file {filepath} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
        try:
            if file.is_file():
                os.chmod(filepath, 0o777)  # Change the file permissions to allow write
                file.unlink()
            else:
                for root, dirs, files in os.walk(filepath):
                    for dir in dirs:
                        os.chmod(os.path.join(root, dir), 0o777)
                    for file in files:
                        os.chmod(os.path.join(root, file), 0o777)
                rmtree(filepath)
        except PermissionError:
            print(f"Unable to remove file {filepath} : Permission Error")
