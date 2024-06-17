"""
mdns_monitor.py

This script acts as a monitor for mDNS service discovery. It discovers services on
the local network and periodically displays the current list of discovered services.
"""

import socket
import sys
import time
from datetime import datetime
from threading import Thread, Event
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, ServiceInfo

class MDNSMonitor:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.services = {}
        self.stop_event = Event()

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
        Periodically display the list of current services.
        """
        while not self.stop_event.wait(10):  # Wait for 10 seconds or until stop_event is set
            print(f"\n{datetime.now()} - Current mDNS Services:")
            for name, info in self.services.items():
                print(f" - {name} at {socket.inet_ntoa(info.addresses[0])}:{info.port}")
            print("Waiting for the next update...")

    def send_mdns_query(self):
        """
        Periodically send an mDNS query.
        """
        while not self.stop_event.wait(60):  # Send query every 60 seconds
            print(f"{datetime.now()} - Sending mDNS query")
            self.zeroconf.send_query('_http._tcp.local.')

    def run(self):
        """
        Run the mDNS monitor by browsing for services and handling their addition
        and removal.
        """
        ServiceBrowser(self.zeroconf, "_http._tcp.local.", handlers=[self.on_service_state_change])
        display_thread = Thread(target=self.display_services)
        query_thread = Thread(target=self.send_mdns_query)
        display_thread.start()
        query_thread.start()
        return display_thread, query_thread

    def close(self):
        """
        Close the Zeroconf instance and clean up.
        """
        self.stop_event.set()
        self.zeroconf.close()

if __name__ == "__main__":
    monitor = MDNSMonitor()
    try:
        display_thread, query_thread = monitor.run()
        print("Press Ctrl+C to exit")
        # Use stop_event.wait() to efficiently wait for an interrupt
        while not monitor.stop_event.wait(1):
            print(f"{datetime.now()} - Checking for new services...")
    except KeyboardInterrupt:
        print("Monitor interrupted by user")
    finally:
        monitor.close()
        display_thread.join()
        query_thread.join()
        print("mDNS monitor stopped")
