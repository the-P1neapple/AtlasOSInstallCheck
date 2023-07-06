import win32serviceutil
import win32service


services_deletion_exceptions = set()

services_reset_exceptions = set()


def get_all_services():
    accessSCM = win32service.SC_MANAGER_ALL_ACCESS
    hscm = win32service.OpenSCManager(None, None, accessSCM)
    service_type = win32service.SERVICE_WIN32
    service_state = win32service.SERVICE_STATE_ALL
    status_handle = win32service.EnumServicesStatus(hscm, service_type, service_state)
    win32service.CloseServiceHandle(hscm)
    return status_handle


def delete_service(service_name):
    try:
        handle = win32serviceutil.SmartOpenService(None, service_name, win32service.SERVICE_ALL_ACCESS)
        win32serviceutil.StopService(service_name)
        win32service.DeleteService(handle)
        win32service.CloseServiceHandle(handle)
        print(f' ==> Deleting service {service_name}')
    except Exception as e:
        print(f'Failed to delete the service {service_name}: {str(e)}')


def checkServiceExistsAndDelete(service_name, skip_prompts):
    services = get_all_services()
    services_names = {service[0] for service in services}
    if service_name in services_names and (skip_prompts or input(f"The service {service_name} exists but should have been removed. Do you want to delete it? (y/n) ") == 'y'):
        delete_service(service_name)


def checkServiceStartupAndReset(service_name, startup_type, skip_prompts):
    if service_name in services_reset_exceptions:
        return
    try:
        startup_type = int(startup_type)
        if startup_type < 0 or startup_type > 4:
            raise ValueError
    except ValueError:
        print(f"Invalid startup type {startup_type}")
        return
    services = get_all_services()
    services_names = {service[0] for service in services}
    if service_name in services_names:
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        handle = win32serviceutil.SmartOpenService(hscm, service_name, win32service.SERVICE_QUERY_CONFIG | win32service.SERVICE_CHANGE_CONFIG)
        service_info = win32service.QueryServiceConfig(handle)
        if service_info[1] != startup_type and (skip_prompts or input(f"The service {service_name} ({service_info[8]}) is set to {service_info[1]} instead of {startup_type}. Do you want to reset it? (y/n) ") == 'y'):
            win32service.ChangeServiceConfig(handle, win32service.SERVICE_NO_CHANGE, startup_type, win32service.SERVICE_NO_CHANGE, None, None, 0, None, None, None, None)
            print(f' ==> Resetting service {service_name} ({service_info[8]}) to {startup_type}')
        win32service.CloseServiceHandle(handle)
        win32service.CloseServiceHandle(hscm)
