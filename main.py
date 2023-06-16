import winreg as reg
import re
import yaml


def getRegistryValue(key, valuename):
    value_value = reg.QueryValueEx(key, valuename)
    return value_value[0]


def setRegistryValue(key, valuename, newvalue):
    reg.SetValueEx(key, valuename, newvalue)


def checkAndResetValue(path, valuename, originalvalue):
    rootdir = path.split('\\')[0]
    initial_key = None
    match rootdir:
        case 'HKCR':
            initial_key = reg.HKEY_CLASSES_ROOT
        case 'HKCU':
            initial_key = reg.HKEY_CURRENT_USER
        case 'HKLM':
            initial_key = reg.HKEY_LOCAL_MACHINE
        case 'HKU':
            initial_key = reg.HKEY_USERS
        case 'HKCG':
            initial_key = reg.HKEY_CURRENT_CONFIG
    if initial_key is None:
        return
    key = reg.OpenKeyEx(initial_key, path[len(rootdir) + 1:] + '\\')
    if key:
        value = getRegistryValue(key, valuename)
        if value != originalvalue and input(f"The registery value {valuename} at {path} is set to {value} instead of {originalvalue}. Do you want to reset it? (y/n)") == 'y':
            setRegistryValue(key, valuename, originalvalue)
        reg.CloseKey(key)


def custom_constructor(loader, tag_suffix, node):
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

def read_YAML_file(filename):
    with open(filename, 'r') as f:
        yaml_str = f.read()
    tags = set(re.findall(r'!([\w]+)', yaml_str))
    for tag in tags:
        yaml.add_multi_constructor(f"!{tag}", custom_constructor)
    data = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return data



yamlfilename = "C:\\Users\\Louis\\Downloads\\Atlas.Playbook.22H2.v0.2\\Configuration\\features\\atlas\\config.yml"
data = read_YAML_file(yamlfilename)
print(data)
