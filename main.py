import winreg as reg
import re
import yaml
import sys
import os
import pathlib
from shutil import rmtree


def getRegistryValue(key, value_name, deletion_detection=False):
    try:
        value_value = reg.QueryValueEx(key, value_name)
    except FileNotFoundError:
        if not deletion_detection:
            print(f"Could not find value {value_name}")
        return None
    return value_value[0]


def setRegistryValue(key, value_name, new_value, datatype):
    regtype = None
    match datatype:
        case 'REG_SZ':
            regtype = reg.REG_SZ
        case 'REG_EXPAND_SZ':
            regtype = reg.REG_EXPAND_SZ
        case 'REG_MULTI_SZ':
            regtype = reg.REG_MULTI_SZ
        case 'REG_DWORD':
            regtype = reg.REG_DWORD
            new_value = int(new_value)
        case 'REG_QWORD':
            regtype = reg.REG_QWORD
            new_value = int(new_value)
        case 'REG_BINARY':
            regtype = reg.REG_BINARY
        case 'REG_NONE':
            regtype = reg.REG_NONE
    if regtype is None:
        raise ValueError(f"Invalid datatype {datatype}")
    reg.SetValueEx(key, value_name, 00, regtype, new_value)


def openRegistryKey(path):
    rootdir = path.split('\\')[0]
    initial_key = None
    match rootdir:
        case 'HKCR':
            initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKEY_CLASSES_ROOT':
            initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKCU':
            initial_key = reg.HKEY_CURRENT_USER
        case 'HKEY_CURRENT_USER':
            initial_key = reg.HKEY_CURRENT_USER
        case 'HKLM':
            initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKEY_LOCAL_MACHINE':
            initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKU':
            initial_key = reg.HKEY_USERS
        case 'HKEY_USERS':
            initial_key = reg.HKEY_USERS
        case 'HKCG':
            initial_key = reg.HKEY_CURRENT_CONFIG
        case 'HKEY_CURRENT_CONFIG':
            initial_key = reg.HKEY_CURRENT_CONFIG
    if initial_key is None:
        raise ValueError(f"Invalid root directory {rootdir}")
    try:
        key = reg.OpenKeyEx(initial_key, path[len(rootdir) + 1:] + '\\', 0, reg.KEY_ALL_ACCESS)
    except PermissionError:
        print(f"Permission denied to open {path}")
        return None
    except FileNotFoundError:
        print(f"Could not find key {path}")
        return None
    return key


def checkAndResetValue(path, value_name, original_value, datatype):
    # Skipping these registry values as these two define the pinned values in the taskbar
    if path == "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Taskband" and (value_name == "FavoritesResolve" or value_name == "Favorites"):
        return
    key = openRegistryKey(path)
    if key:
        value = getRegistryValue(key, value_name)
        if datatype == 'REG_BINARY':
            original_value = bytes.fromhex(original_value)
        if (str(value) != str(original_value) and not (str(original_value) == "" and str(value) == "None")) and input(f"The registery value {value_name} at {path} is set to {str(value)} instead of {str(original_value)}. Do you want to reset it? (y/n) ") == 'y':
            print(f"Resetting registery value {value_name} at {path} to {original_value}")
            setRegistryValue(key, value_name, original_value, datatype)

        reg.CloseKey(key)


def checkKeyExistsAndDelete(path):
    key = openRegistryKey(path)
    if key and input(f"The registery key {path} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y':
        try:
            reg.DeleteKey(key, "")
            print(f"Deleting registery key {path}")
        except PermissionError:
            print(f"Cannot delete regitry key {path}: Permission Error")
    reg.CloseKey(key)


def checkValueExistsAndDelete(path, value_name):
    key = openRegistryKey(path)
    if key:
        value = getRegistryValue(key, value_name, True)
        if value is not None and input(f"The registery value {value_name} at {path} is set to {str(value)} but should have been removed. Do you want to delete it? (y/n) ") == 'y':
            reg.DeleteValue(key, value_name)
            print(f"Deleting registery value {value_name} at {path}")
        reg.CloseKey(key)


def checkFileExistsAndDelete(filepath):
    file = pathlib.Path(filepath)
    if file.exists() and input(f"The file {filepath} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y':
        try:
            rmtree(filepath)
        except PermissionError:
            print(f"Unable to remove file {filepath} : Permission Error")


def customConstructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        try:
            value = list(loader.construct_yaml_map(node))[0]
        except ValueError:
            value = ""
    elif isinstance(node, yaml.ScalarNode):
        value = loader.construct_yaml_str(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_yaml_seq(node)
    else:
        raise yaml.constructor.ConstructorError(
            None, None, f'Unsupported node type: {node.id}', node.start_mark)
    name = node.tag[1:].strip(':')
    return {name: value}


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



def readYamlFile(filename):
    with open(filename, 'r') as f:
        yaml_str = f.read()
    tags = set(re.findall(r'!([\w]+)', yaml_str))
    for tag in tags:
        yaml.add_multi_constructor(f"!{tag}", customConstructor)
    data = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return data


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
