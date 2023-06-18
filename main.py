import winreg as reg
import re
import yaml


def getRegistryValue(key, value_name):
    try:
        value_value = reg.QueryValueEx(key, value_name)
    except FileNotFoundError:
        print(f"Could not find value {value_name}")
        return None
    return value_value[0]


def setRegistryValue(key, value_name, new_value, datatype):
    reg.SetValueEx(key, value_name, 1, datatype, new_value)


def checkAndResetValue(path, value_name, original_value, datatype):
    rootdir = path.split('\\')[0]
    initial_key = None
    match rootdir:
        case 'HKCR': initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKEY_CLASSES_ROOT': initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKCU': initial_key = reg.HKEY_CURRENT_USER
        case 'HKEY_CURRENT_USER': initial_key = reg.HKEY_CURRENT_USER
        case 'HKLM': initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKEY_LOCAL_MACHINE': initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKU': initial_key = reg.HKEY_USERS
        case 'HKEY_USERS': initial_key = reg.HKEY_USERS
        case 'HKCG': initial_key = reg.HKEY_CURRENT_CONFIG
        case 'HKEY_CURRENT_CONFIG': initial_key = reg.HKEY_CURRENT_CONFIG

    if initial_key is None:
        raise ValueError(f"Invalid root directory {rootdir}")
    try:
        key = reg.OpenKeyEx(initial_key, path[len(rootdir) + 1:] + '\\')
    except PermissionError:
        print(f"Permission denied to open {path}")
        return
    except FileNotFoundError:
        print(f"Could not find key {path}")
        return
    if key:
        value = getRegistryValue(key, value_name)
        if datatype == 'REG_BINARY':
            original_value = bytes.fromhex(original_value)
        if str(value) != str(original_value) and input(f"The registery value {value_name} at {path} is set to {str(value)} instead of {str(original_value)}. Do you want to reset it? (y/n) ") == 'y':
            print(f"Resetting registery value {value_name} at {path} to {original_value}")

            print("WARNING: Registry datatypes not yet supported, cannot reset value")

            #setRegistryValue(key, value_name, original_value)
        reg.CloseKey(key)


def checkValueExistsAndDelete(path, value_name):
    rootdir = path.split('\\')[0]
    initial_key = None
    match rootdir:
        case 'HKCR': initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKEY_CLASSES_ROOT': initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKCU': initial_key = reg.HKEY_CURRENT_USER
        case 'HKEY_CURRENT_USER': initial_key = reg.HKEY_CURRENT_USER
        case 'HKLM': initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKEY_LOCAL_MACHINE': initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKU': initial_key = reg.HKEY_USERS
        case 'HKEY_USERS': initial_key = reg.HKEY_USERS
        case 'HKCG': initial_key = reg.HKEY_CURRENT_CONFIG
        case 'HKEY_CURRENT_CONFIG': initial_key = reg.HKEY_CURRENT_CONFIG
    if initial_key is None:
        raise ValueError(f"Invalid root directory {rootdir}")
    try:
        key = reg.OpenKeyEx(initial_key, path[len(rootdir) + 1:] + '\\')
    except PermissionError:
        print(f"Permission denied to open {path}")
        return
    except FileNotFoundError:
        print(f"Could not find key {path}")
        return
    if key:
        value = getRegistryValue(key, value_name)
        if value is not None and input(f"The registery value {value_name} at {path} is set to {str(value)} but should have been removed. Do you want to delete it? (y/n) ") == 'y':
            print(f"Deleting registery value {value_name} at {path}")
            reg.DeleteValue(key, value_name)
        reg.CloseKey(key)


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
            pass
        elif 'registryValue' in keys:
            if action['registryValue'].get('operation') == 'delete':
                checkValueExistsAndDelete(action['registryValue']['path'], action['registryValue']['value'])
            try:
                checkAndResetValue(action['registryValue']['path'], action['registryValue']['value'],
                                   action['registryValue']['data'], action['registryValue']['type'])
            except KeyError as e:
                print(f"Missing key {e} in action {action}")
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


yaml_filename = "C:\\Users\\Louis\\Downloads\\Atlas.Playbook.22H2.v0.2\\Configuration\\features\\atlas\\config.yml"
data = readYamlFile(yaml_filename)
processActions(data)
