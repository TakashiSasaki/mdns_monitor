import socket
import sys
from zeroconf import ServiceInfo, Zeroconf

# mDNSサービス登録
def register_mdns_service(port):
    zeroconf = Zeroconf()
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "MyService._http._tcp.local.",
        addresses=[socket.inet_aton("192.168.1.100")],  # 自分のIPアドレスを設定
        port=port,
        properties={"path": "/"}
    )

    zeroconf.register_service(service_info)
    print(f"mDNS service registered on port {port}")
    return zeroconf, service_info

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mdns.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    zeroconf = None
    service_info = None
    try:
        zeroconf, service_info = register_mdns_service(port)
        print("Press Ctrl+C to exit")
        while True:
            pass  # サービスが登録されたままにするために無限ループで待機
    except KeyboardInterrupt:
        print("Service interrupted by user")
    except PermissionError as e:
        print(f"Permission error: {e}")
    finally:
        if zeroconf and service_info:
            zeroconf.unregister_service(service_info)
            zeroconf.close()
            print("mDNS service unregistered")
