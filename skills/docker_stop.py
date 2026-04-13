"""
/synology-docker-stop <container-name> — Stop a running Docker container.
Requires explicit confirmation — this immediately kills the container process.
API: SYNO.Docker.Container v1 stop
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def stop_container(host, sid, name):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "stop",
            "name": name,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_stop.py <container-name>")
        print("       docker_stop.py <container-name> --yes  (skip confirmation)")
        sys.exit(1)

    name = sys.argv[1]
    skip_confirm = "--yes" in sys.argv

    if not skip_confirm:
        confirm = input(f"Stop container '{name}'? This kills the process immediately. Type YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    host, sid = get_session()
    try:
        result = stop_container(host, sid, name)
        if result.get("success"):
            print(f"Stopped: {name}")
        else:
            code = result.get("error", {}).get("code", "?")
            print(f"Failed (error {code}). Check the container name with: python skills/docker.py")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
