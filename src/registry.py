import winreg as reg

# Note : the following values and keys are ignored because they are recreated by the system at each reboot
values_exeptions= {
    "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Taskband": ["FavoritesResolve", "Favorites"],
    "HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger\ReadyBoot" : "Start",
    "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\SessionData": "AllowLockScreen",
}

keys_exceptions = {
    "HKCU\SOFTWARE\Microsoft\Edge",
    "HKCU\SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU",
    "HKCU\SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags",
    "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
}


def delete_key_with_sub_keys(key):
    try:
        i = 0
        while True:
            subkey_name = reg.EnumKey(key, i)
            subkey = reg.OpenKey(key, subkey_name, 0, reg.KEY_ALL_ACCESS)
            delete_key_with_sub_keys(subkey)
            reg.DeleteKey(key, subkey_name)
            reg.CloseKey(subkey)
            i += 1
    except WindowsError:
        pass


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
        #print(f"Could not find key {path}")
        return None
    return key


def checkAndResetValue(path, value_name, original_value, datatype, skip_prompts):
    # Skipping values that define user customized values (e.g. taskbar shortcuts)
    if values_exeptions.get(path) and value_name in values_exeptions.get(path):
        return
    if (r"HKCU\SOFTWARE\Classes\." in path or r"HKLM\SOFTWARE\Classes\." in path) and path.count('\\') == 3 and value_name == "":
        return
    key = openRegistryKey(path)
    if key:
        value = getRegistryValue(key, value_name)
        if value is None:
            reg.CloseKey(key)
            return
        if datatype == 'REG_BINARY':
            original_value = bytes.fromhex(original_value)
        if (str(value) != str(original_value) and not (str(original_value) == "" and str(value) == "None")) and\
                (skip_prompts or input(f"The registery value {value_name} at {path} is set to {str(value)} instead of {str(original_value)}. Do you want to reset it? (y/n) ") == 'y'):
            print(f" ==> Resetting registery value {value_name} at {path} to {original_value}")
            setRegistryValue(key, value_name, original_value, datatype)

        reg.CloseKey(key)


def checkKeyExistsAndDelete(path, skip_prompts):
    if path in keys_exceptions:
        return
    key = openRegistryKey(path)
    if key and (skip_prompts or input(f"The registery key {path} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
        try:
            delete_key_with_sub_keys(key)
            reg.DeleteKey(key, "")
            print(f" ==> Deleting registery key {path}")
        except PermissionError:
            print(f"Cannot delete regitry key {path}: Permission Error")
    reg.CloseKey(key)


def checkValueExistsAndDelete(path, value_name, skip_prompts):
    key = openRegistryKey(path)
    if key:
        value = getRegistryValue(key, value_name, True)
        if value is not None and (skip_prompts or input(f"The registery value {value_name} at {path} is set to {str(value)} but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
            reg.DeleteValue(key, value_name)
            print(f" ==> Deleting registery value {value_name} at {path}")
        reg.CloseKey(key)
