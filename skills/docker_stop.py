"""
/synology-docker-stop <container-name> — Stop a running Docker container.
API: SYNO.Docker.Container
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def stop_container(host, sid, name):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "stop",
            "name": f'"{name}"',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_stop.py <container-name>")
        sys.exit(1)
    name = sys.argv[1]
    host, sid = get_session()
    try:
        result = stop_container(host, sid, name)
        if result.get("success"):
            print(f"Stopped: {name}")
        else:
            print(f"Failed: {result.get('error')}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
