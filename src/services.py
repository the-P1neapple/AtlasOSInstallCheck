import win32serviceutil
import win32service


def list_all_services():
    accessSCM = win32service.SC_MANAGER_ALL_ACCESS
    hscm = win32service.OpenSCManager(None, None, accessSCM)
    service_type = win32service.SERVICE_WIN32
    service_state = win32service.SERVICE_STATE_ALL
    status_handle = win32service.EnumServicesStatus(hscm, service_type, service_state)
    for (short_name, desc, status) in status_handle:
        print(f'{short_name} - {desc}')
    win32service.CloseServiceHandle(hscm)


def delete_service(service_name):
    try:
        handle = win32serviceutil.SmartOpenService(None, service_name, win32service.SERVICE_ALL_ACCESS)
        win32serviceutil.StopService(service_name)
        win32service.DeleteService(handle)
        win32service.CloseServiceHandle(handle)
        print(f' ==> Deleting service {service_name}')
    except Exception as e:
        print(f'Failed to delete the service {service_name}: {str(e)}')

