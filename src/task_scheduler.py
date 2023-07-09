import win32com.client
from subprocess import run, DEVNULL


tasks_folder_exceptions = {
    r"\Microsoft\Windows\UpdateOrchestrator",
}

task_exception = {
    r"\Microsoft\Windows\WindowsUpdate\Scheduled Start"
}


def checkTasksFolderExistsAndDelete(path, skip_prompts):
    if path in tasks_folder_exceptions:
        return
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    command = (
        f'powershell.exe -Command "'
        f'Get-ScheduledTask -TaskPath \'{path}\\*\' | Unregister-ScheduledTask -Confirm:$false'
        f'"'
    )
    try:
        task_folder = scheduler.GetFolder(path)
        if skip_prompts or input(f"The tasks folder {path} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y':
            run(command, check=True, shell=True, stdout=DEVNULL)
            run(f'schtasks /Delete /TN "{path}" /F', check=True, shell=True, stdout=DEVNULL)
            print(f' ==> Deleting tasks folder {path}')
    except:
        pass


def checkTaskExistsAndDelete(path, skip_prompts):
    if path in task_exception:
        return
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    try:
        task_folder_path, task_name = path.rsplit("\\", 1)
        task_folder = scheduler.GetFolder(task_folder_path)
        task = task_folder.GetTask(task_name)
        if skip_prompts or input(f"The task {path} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y':
            run(f'schtasks /Delete /TN "{path}" /F', check=True, shell=True, stdout=DEVNULL)
            print(f' ==> Deleting task {path}')
    except:
        pass
