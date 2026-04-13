"""
/synology-docker — List all Docker containers: status, image, uptime.
API: SYNO.Docker.Container
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def list_containers(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "list",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        data = list_containers(host, sid)
        containers = data.get("data", {}).get("containers", [])
        print(f"=== Docker Containers ({len(containers)}) ===\n")
        print(f"  {'NAME':<35} {'STATUS':<12} {'IMAGE'}")
        print("  " + "-" * 75)
        for c in sorted(containers, key=lambda x: x.get("name", "")):
            name = c.get("name", "?")
            status = c.get("status", "?")
            image = c.get("image", "?")
            print(f"  {name:<35} {status:<12} {image}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
