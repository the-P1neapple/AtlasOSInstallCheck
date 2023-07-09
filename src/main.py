from sys import argv
from zipfile import ZipFile
from registry import checkKeyExistsAndDelete, checkValueExistsAndDelete, checkAndResetValue
from files import checkFileExistsAndDelete
from yaml_parser import readYamlFile, readYaml
from services import checkServiceStartupAndReset, checkServiceExistsAndDelete
from task_scheduler import checkTaskExistsAndDelete, checkTasksFolderExistsAndDelete


checks_state = {"registry": False, "files": False, "services": False, "schdtasks": False}
help_msg = """Usage:run.cmd <path to Atlas Playbook Directory> [-r] [-f] [-s] [-t] [-y]
To get the Atlas Playbook Directory, download the Atlas Playbook https://atlasos.net/ and extract it (password: malte)"""
skip_prompts = False


def processActions(yaml_content):
    actions = yaml_content['actions']
    for action in actions:
        keys = action.keys()
        if 'registryKey' in keys and checks_state['registry']:
            checkKeyExistsAndDelete(action['registryKey']['path'], skip_prompts)
        elif 'registryValue' in keys and checks_state['registry']:
            if action['registryValue'].get('operation') == 'delete':
                checkValueExistsAndDelete(action['registryValue']['path'], action['registryValue']['value'], skip_prompts)
                continue
            try:
                checkAndResetValue(action['registryValue']['path'], action['registryValue']['value'],
                                   action['registryValue']['data'], action['registryValue']['type'], skip_prompts)
            except KeyError as e:
                print(f"Missing key {e} in action {action}")
        elif 'file' in keys and checks_state['files']:
            checkFileExistsAndDelete(action['file']['path'], skip_prompts)
        elif 'service' in keys and checks_state['services']:
            if action['service'].get('operation') == 'change':
                checkServiceStartupAndReset(action['service']['name'], action['service']['startup'], skip_prompts)
            elif action['service'].get('operation') == 'delete':
                checkServiceExistsAndDelete(action['service']['name'], skip_prompts)
        elif 'scheduledTask' in keys and checks_state['schdtasks']:
            if action['scheduledTask'].get('operation') == 'delete':
                checkTaskExistsAndDelete(action['scheduledTask']['path'], skip_prompts)
            elif action['scheduledTask'].get('operation') == 'deleteFolder':
                checkTasksFolderExistsAndDelete(action['scheduledTask']['path'], skip_prompts)
        else:
            continue

def parse_args():
    global skip_prompts
    args = argv[1:]
    if len(args) < 1 or ('-h' in args or '--help' in args):
        print(help_msg)
        exit(1)
    patharg = None
    for arg in args:
        if arg.startswith("-"):
            match arg:
                case "-r":
                    checks_state["registry"] = True
                case "-f":
                    checks_state["files"] = True
                case "-s":
                    checks_state["services"] = True
                case "-t":
                    checks_state["schdtasks"] = True
                case "-y":
                    skip_prompts = True
                case _:
                    print(f"Unknown argument: {arg}")
                    exit(1)
        else:
            patharg = arg
    if patharg is None:
        print(help_msg)
        exit(1)
    if True not in checks_state.values():
        for k in checks_state.keys():
            checks_state[k] = True
    return patharg


def main():
    config_path = parse_args()
    try:
        zip = ZipFile(config_path)
        config_dir_content = zip.namelist()
    except FileNotFoundError:
        print("Could not find the configuration directory. Please make sure you are pointing to the correct directory")
        exit(1)
    if "Configuration/custom.yml" not in config_dir_content:
        print("Could not find custom.yml in the configuration directory. Please make sure you are pointing to the correct directory")
        exit(1)
    config_data = readYaml(zip.read('Configuration/custom.yml'), 'custom.yml')
    yml_files_list = config_data['features']
    if "tweaks.yml" in yml_files_list:
        yml_files_list.remove("tweaks.yml")
        tweaks_data = readYaml(zip.read('Configuration/tweaks.yml'), 'tweaks.yml')
        yml_files_list.extend(tweaks_data['features'])
    for file in yml_files_list:
        file = file.replace("\\","/")
        yml_file = readYaml(zip.read('Configuration/' + file), file)
        processActions(yml_file)
    exit(0)


main()
