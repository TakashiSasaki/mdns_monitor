"""
mdns_monitor.py

This script acts as a monitor for mDNS service discovery. It discovers services on
the local network and provides an interactive shell to display the current list of
discovered services and force sending mDNS queries.
"""

import socket
import sys
from datetime import datetime
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ServiceInfo
import cmd

class MDNSMonitor:
    def __init__(self, service_types):
        self.zeroconf = Zeroconf()
        self.services = {}
        self.service_types = service_types
        self.browsers = []
        self.create_browsers()

    def create_browsers(self):
        """
        Create new ServiceBrowser instances for each service type.
        """
        for service_type in self.service_types:
            browser = ServiceBrowser(self.zeroconf, service_type, handlers=[self.on_service_state_change])
            self.browsers.append(browser)

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """
        Handle state changes of discovered services.
        """
        if state_change is ServiceStateChange.Added:
            self.add_service(zeroconf, service_type, name)
            print(f"{datetime.now()} - Service {name} ({service_type}) has been added by ServiceBrowser")
        elif state_change is ServiceStateChange.Removed:
            self.remove_service(zeroconf, service_type, name)
            print(f"{datetime.now()} - Service {name} ({service_type}) has been removed by ServiceBrowser")

    def add_service(self, zeroconf, service_type, name):
        """
        Add a discovered service to the local list.
        """
        info = zeroconf.get_service_info(service_type, name)
        if info:
            self.services[name] = info
            print(f"{datetime.now()} - Service {name} ({service_type}) added")

    def remove_service(self, zeroconf, service_type, name):
        """
        Remove a service from the local list.
        """
        if name in self.services:
            del self.services[name]
            print(f"{datetime.now()} - Service {name} ({service_type}) removed")

    def display_services(self):
        """
        Display the list of current known services.
        """
        print(f"\n{datetime.now()} - Current known mDNS Services:")
        for name, info in self.services.items():
            print(f" - {name} at {socket.inet_ntoa(info.addresses[0])}:{info.port} ({info.type})")
        print("")

    def close(self):
        """
        Close the Zeroconf instance and clean up.
        """
        self.zeroconf.close()

class MDNSCmd(cmd.Cmd):
    intro = 'Welcome to the mDNS monitor. Type help or ? to list commands.\n'
    prompt = '(mdns_monitor) '

    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor

    def do_exit(self, line):
        """Exit the monitor."""
        print("Exiting mDNS monitor...")
        return True

    def emptyline(self):
        """When an empty line is entered, display the list of current known services."""
        self.monitor.display_services()

    def do_renew(self, line):
        """Renew the ServiceBrowser instances."""
        print(f"{datetime.now()} - Renewing ServiceBrowser instances")
        self.monitor.create_browsers()

if __name__ == "__main__":
    service_types = [
        "_http._tcp.local.", "_https._tcp.local.", "_ftp._tcp.local.", "_ssh._tcp.local.",
        "_smb._tcp.local.", "_printer._tcp.local.", "_ipp._tcp.local.", "_airplay._tcp.local.",
        "_raop._tcp.local.", "_afpovertcp._tcp.local.", "_nfs._tcp.local.", "_daap._tcp.local.",
        "_dacp._tcp.local.", "_hue._tcp.local.", "_hap._tcp.local.", 
        "_googlecast._tcp.local.",  # Google Home and Chromecast
        "_amazon._tcp.local.",      # Amazon Echo
        "_fuego._tcp.local."        # FireTV
    ]
    monitor = MDNSMonitor(service_types)
    cmd_interface = MDNSCmd(monitor)
    try:
        cmd_interface.cmdloop()
    except KeyboardInterrupt:
        print("\nMonitor interrupted by user")
    finally:
        monitor.close()
        print("mDNS monitor stopped")
