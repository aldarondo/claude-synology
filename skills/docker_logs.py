"""
/synology-docker-logs <container-name> [--lines N] — Tail recent logs from a container.
API: SYNO.Docker.Container.Log
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def get_logs(host, sid, name, lines=50):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Container.Log",
            "version": "1",
            "method": "get",
            "name": f'"{name}"',
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
        logs = data.get("data", {}).get("log", "")
        print(f"=== Logs: {name} (last {lines} lines) ===\n")
        print(logs)
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
