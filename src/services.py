import win32serviceutil
import win32service


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
    services = get_all_services()
    services_names = {service[0] for service in services}
    if service_name in services_names:
        handle = win32serviceutil.SmartOpenService(None, service_name, win32service.SERVICE_ALL_ACCESS)
        service_info = win32service.QueryServiceConfig(handle)
        print(service_info[1], "||", win32service.SERVICE_AUTO_START, win32service.SERVICE_BOOT_START, win32service.SERVICE_DEMAND_START, win32service.SERVICE_DISABLED, win32service.SERVICE_SYSTEM_START)
        return
        if service_info[1] != startup_type and (skip_prompts or input(f"The service {service_name} is set to {service_info[1]} instead of {startup_type}. Do you want to reset it? (y/n) ") == 'y'):
            pass


checkServiceStartupAndReset("dcsvc", 1, False)
