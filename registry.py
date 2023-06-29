import winreg as reg
from main import skip_prompts


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
        if (str(value) != str(original_value) and not (str(original_value) == "" and str(value) == "None")) and\
                (skip_prompts or input(f"The registery value {value_name} at {path} is set to {str(value)} instead of {str(original_value)}. Do you want to reset it? (y/n) ") == 'y'):
            print(f"Resetting registery value {value_name} at {path} to {original_value}")
            setRegistryValue(key, value_name, original_value, datatype)

        reg.CloseKey(key)


def checkKeyExistsAndDelete(path):
    key = openRegistryKey(path)
    if key and (skip_prompts or input(f"The registery key {path} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
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
        if value is not None and (skip_prompts or input(f"The registery value {value_name} at {path} is set to {str(value)} but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
            reg.DeleteValue(key, value_name)
            print(f"Deleting registery value {value_name} at {path}")
        reg.CloseKey(key)
