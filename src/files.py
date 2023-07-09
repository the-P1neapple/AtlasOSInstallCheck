from pathlib import Path
from shutil import rmtree
from os import chmod, path, walk
import psutil

# Note : the following files and folders are ignored because they are recreated by the system at each reboot
files_exeptions = {
    "C:\\Windows\\SoftwareDistribution"
}


def killFileProcess(filename):
    if filename.endswith('.exe'):
        for proc in psutil.process_iter(['pid']):
            try:
                p = psutil.Process(proc.pid)
                if p.exe() == filename:
                    print(f" ==> Killing process {p.name()} (PID {p.pid})")
                    p.kill()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass


def checkFileExistsAndDelete(filepath, skip_prompts):
    if filepath in files_exeptions:
        return
    file = Path(filepath)
    if file.exists() and (skip_prompts or input(f"The file {filepath} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
        try:
            if file.is_file():
                killFileProcess(filepath)
                chmod(filepath, 0o777)
                print(f" ==> Removing file {filepath}")
                file = Path(filepath)
                file.unlink()
            else:
                for root, dirs, files in walk(filepath):
                    for d in dirs:
                        chmod(path.join(root, d), 0o777)
                    for file in files:
                        killFileProcess(path.join(root, file))
                        chmod(path.join(root, file), 0o777)
                rmtree(filepath)
                print(f" ==> Removing directory {filepath}")
        except PermissionError:
            print(f"Unable to remove file {filepath} : Permission Error")
