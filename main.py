import sys
import os
from registry import checkKeyExistsAndDelete, checkValueExistsAndDelete, checkAndResetValue
from files import checkFileExistsAndDelete
from yaml_parser import readYamlFile


def processActions(yaml_content):
    actions = yaml_content['actions']
    for action in actions:
        keys = action.keys()
        if 'registryKey' in keys:
            checkKeyExistsAndDelete(action['registryKey']['path'])
        elif 'registryValue' in keys:
            if action['registryValue'].get('operation') == 'delete':
                checkValueExistsAndDelete(action['registryValue']['path'], action['registryValue']['value'])
                continue
            try:
                checkAndResetValue(action['registryValue']['path'], action['registryValue']['value'],
                                   action['registryValue']['data'], action['registryValue']['type'])
            except KeyError as e:
                print(f"Missing key {e} in action {action}")
        elif 'file' in keys:
            checkFileExistsAndDelete(action['file']['path'])
        else:
            print(f"Unsupported action: {list(keys)[0]}")


def main():
    args = sys.argv[1:]
    if len(args) != 1 or (args[0] == '-h' or args[0] == '--help'):
        print("Usage: python3 main.py <path to Atlas Playbook Directory>\nTo get the Atlas Playbook Directory, download the Atlas Playbook https://atlasos.net/ and extract it (password: malte)")
        exit(1)
    config_path = args[0] + "\\Configuration\\"
    config_dir_content = os.listdir(config_path)
    if "custom.yml" not in config_dir_content:
        print("Could not find custom.yml in the configuration directory. Please make sure you are pointing to the correct directory")
        exit(1)
    config_data = readYamlFile(config_path + "custom.yml")
    yml_files_list = config_data['features']
    for file in yml_files_list:
        yml_file = readYamlFile(config_path + file)
        processActions(yml_file)
    exit(0)


main()
