"""
/synology-docker-logs <container-name> [--lines N] — Tail recent logs from a container.
API: SYNO.Docker.Container.Log v1 get

Note: The DSM Docker Log API (error 114) does not reliably support log streaming
for Docker Compose-managed containers on Container Manager 24.x. If this returns
an error, view logs directly in DSM > Container Manager > Containers > [name] > Log.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def get_logs(host, sid, name, lines=50):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container.Log",
            "version": "1",
            "method": "get",
            "name": name,
            "tail": lines,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_logs.py <container-name> [--lines N]")
        sys.exit(1)

    name = sys.argv[1]
    lines = 50
    if "--lines" in sys.argv:
        idx = sys.argv.index("--lines")
        lines = int(sys.argv[idx + 1])

    host, sid = get_session()
    try:
        data = get_logs(host, sid, name, lines)
        if data.get("success"):
            log = data.get("data", {}).get("log", "")
            print(f"=== Logs: {name} (last {lines} lines) ===\n")
            print(log if log else "(no log output)")
        else:
            code = data.get("error", {}).get("code", "?")
            print(f"Log retrieval failed (error {code}).")
            print()
            print("The DSM Docker Log API does not support log streaming for")
            print("Docker Compose containers in Container Manager 24.x.")
            print()
            print("To view logs, open DSM and go to:")
            print("  Container Manager > Containers > select container > Log tab")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
