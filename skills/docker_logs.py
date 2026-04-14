"""
synology docker logs <container-name> [--lines N]
  Show recent logs from a Docker container.
  Tries the HTTP API first; falls back to SSH `docker logs` for Compose containers
  (Container Manager 24.x does not support the log API for Compose containers).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout
from lib.ssh import get_client, sudo_run, DOCKER


def get_logs_api(host, sid, name, lines):
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


def get_logs_ssh(name, lines):
    client = get_client()
    try:
        out = sudo_run(client,
            f"{DOCKER} logs --tail={lines} {name} 2>&1",
            timeout=30)
        return out
    finally:
        client.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_logs.py <container-name> [--lines N]")
        sys.exit(1)

    name  = sys.argv[1]
    lines = 50
    if "--lines" in sys.argv:
        idx   = sys.argv.index("--lines")
        lines = int(sys.argv[idx + 1])

    host, sid = get_session()
    try:
        data = get_logs_api(host, sid, name, lines)
        if data.get("success"):
            log = data.get("data", {}).get("log", "")
            print(f"=== Logs: {name} (last {lines} lines, via API) ===\n")
            print(log if log else "(no log output)")
            return

        # API failed — fall back to SSH
        code = data.get("error", {}).get("code", "?")
        if code == 114:
            print(f"=== Logs: {name} (last {lines} lines, via SSH) ===\n")
            log = get_logs_ssh(name, lines)
            if not log or "No such container" in log:
                print(f"Container '{name}' not found.")
            else:
                print(log)
        else:
            print(f"Log retrieval failed (error {code}).")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
