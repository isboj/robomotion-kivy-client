from connection_status.status_manager import StatusManager

status_manager = StatusManager()
status_manager.api_v0.can_use = True
print(status_manager.api_v0.print_status())
