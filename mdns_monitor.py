"""
mdns_monitor.py

This script acts as a monitor for mDNS service discovery. It discovers services on
the local network and provides an interactive shell to display the current list of
discovered services and force sending mDNS queries.
"""

import socket
import sys
from datetime import datetime
from threading import Event
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ServiceInfo
import cmd

class MDNSMonitor:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.services = {}
        self.stop_event = Event()
        self.create_browser()

    def create_browser(self):
        """
        Create a new ServiceBrowser instance.
        """
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", handlers=[self.on_service_state_change])

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """
        Handle state changes of discovered services.
        """
        if state_change is ServiceStateChange.Added:
            self.add_service(zeroconf, service_type, name)
            print(f"{datetime.now()} - Service {name} has been added by ServiceBrowser")
        elif state_change is ServiceStateChange.Removed:
            self.remove_service(zeroconf, service_type, name)
            print(f"{datetime.now()} - Service {name} has been removed by ServiceBrowser")

    def add_service(self, zeroconf, service_type, name):
        """
        Add a discovered service to the local list.
        """
        info = zeroconf.get_service_info(service_type, name)
        if info:
            self.services[name] = info
            print(f"{datetime.now()} - Service {name} added")

    def remove_service(self, zeroconf, service_type, name):
        """
        Remove a service from the local list.
        """
        if name in self.services:
            del self.services[name]
            print(f"{datetime.now()} - Service {name} removed")

    def display_services(self):
        """
        Display the list of current services.
        """
        print(f"\n{datetime.now()} - Current mDNS Services:")
        for name, info in self.services.items():
            print(f" - {name} at {socket.inet_ntoa(info.addresses[0])}:{info.port}")
        print("")

    def close(self):
        """
        Close the Zeroconf instance and clean up.
        """
        self.stop_event.set()
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
        """When an empty line is entered, display the list of current services."""
        self.monitor.display_services()

    def do_renew(self, line):
        """Renew the ServiceBrowser instance."""
        print(f"{datetime.now()} - Renewing ServiceBrowser")
        self.monitor.create_browser()

if __name__ == "__main__":
    monitor = MDNSMonitor()
    cmd_interface = MDNSCmd(monitor)
    try:
        cmd_interface.cmdloop()
    except KeyboardInterrupt:
        print("\nMonitor interrupted by user")
    finally:
        monitor.close()
        print("mDNS monitor stopped")
