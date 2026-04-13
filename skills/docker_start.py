"""
/synology-docker-start <container-name> — Start a stopped Docker container.
API: SYNO.Docker.Container v1 start
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def start_container(host, sid, name):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "start",
            "name": name,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_start.py <container-name>")
        sys.exit(1)

    name = sys.argv[1]
    host, sid = get_session()
    try:
        # Verify container exists first
        data = api_get(host, sid, "SYNO.Docker.Container", "1", "list", limit=100, offset=0)
        containers = {c.get("name"): c for c in data.get("data", {}).get("containers", [])}

        if name not in containers:
            print(f"Container '{name}' not found.")
            print("Available containers:")
            for cname, c in sorted(containers.items()):
                running = c.get("State", {}).get("Running", False)
                print(f"  {'+ ' if running else '- '}{cname}")
            return

        c = containers[name]
        if c.get("State", {}).get("Running"):
            print(f"'{name}' is already running ({c.get('up_status', '')})")
            return

        result = start_container(host, sid, name)
        if result.get("success"):
            print(f"Started: {name}")
        else:
            code = result.get("error", {}).get("code", "?")
            print(f"Failed (error {code}).")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
