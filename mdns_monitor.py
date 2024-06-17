"""
mdns_monitor.py

This script acts as a monitor for mDNS service discovery. It discovers services on
the local network and provides an interactive shell to display the current list of
discovered services and force sending mDNS queries.
"""

import socket
import sys
from datetime import datetime
from threading import Thread, Event
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ServiceInfo
import cmd

class MDNSMonitor:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.services = {}
        self.stop_event = Event()
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

    def send_mdns_query(self):
        """
        Periodically send an mDNS query.
        """
        while not self.stop_event.wait(60):  # Send query every 60 seconds
            print(f"{datetime.now()} - Sending mDNS query")
            self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", handlers=[self.on_service_state_change])

    def run(self):
        """
        Run the mDNS monitor by starting the cmd loop and handling service state changes.
        """
        query_thread = Thread(target=self.send_mdns_query)
        query_thread.start()
        return query_thread

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

    def do_query(self, line):
        """Force sending an mDNS query."""
        print(f"{datetime.now()} - Sending mDNS query")
        self.monitor.browser = ServiceBrowser(self.monitor.zeroconf, "_http._tcp.local.", handlers=[self.monitor.on_service_state_change])

    def completenames(self, text, line, begidx, endidx):
        """
        Enable command completion.
        """
        return [name[len('do_'):] for name in self.get_names() if name.startswith('do_' + text)]

    def completedefault(self, text, line, begidx, endidx):
        """
        Provide default completion behavior.
        """
        return [name[len('do_'):] for name in self.get_names() if name.startswith('do_')]

if __name__ == "__main__":
    monitor = MDNSMonitor()
    cmd_interface = MDNSCmd(monitor)
    try:
        query_thread = monitor.run()
        cmd_interface.cmdloop()
    except KeyboardInterrupt:
        print("\nMonitor interrupted by user")
    finally:
        monitor.close()
        query_thread.join()
        print("mDNS monitor stopped")
