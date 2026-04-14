"""
synology network
  Show network interfaces, IPs, gateway, and DNS on the NAS.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, api_get, logout


def main():
    host, sid = get_session()
    try:
        # Interface list (IPs, speeds, status)
        iface_data = api_get(host, sid, "SYNO.Core.Network.Interface", 1, "list")
        # Global network config (gateway, DNS)
        net_data = api_get(host, sid, "SYNO.Core.Network", 1, "get")

        print("=== Network ===\n")

        if iface_data.get("success"):
            interfaces = iface_data.get("data", [])
            connected = [i for i in interfaces if i.get("status") == "connected"]
            other     = [i for i in interfaces if i.get("status") != "connected"]

            for iface in connected + other:
                name   = iface.get("ifname", "?")
                ip     = iface.get("ip", "")
                mask   = iface.get("mask", "")
                speed  = iface.get("speed", 0)
                status = iface.get("status", "?")
                dhcp   = "DHCP" if iface.get("use_dhcp") else "static"
                itype  = iface.get("type", "")

                ip_str = f"{ip}/{mask}" if ip and mask else ip or "(no IP)"
                speed_str = f"{speed}M" if speed else ""
                tag = "+" if status == "connected" else "-"

                print(f"  {tag} {name:<8} {ip_str:<22} {dhcp:<7} {speed_str:<6} [{status}]")

        if net_data.get("success"):
            d = net_data.get("data", {})
            gateway = d.get("gateway", "")
            dns1    = d.get("dns_primary", "")
            dns2    = d.get("dns_secondary", "")
            hostname = d.get("server_name", "")

            print()
            if hostname:
                print(f"  Hostname:   {hostname}")
            if gateway:
                print(f"  Gateway:    {gateway}")
            if dns1 or dns2:
                dns = ", ".join(filter(None, [dns1, dns2]))
                print(f"  DNS:        {dns}")

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
