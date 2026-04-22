"""
synology docker logs <container-name> [--lines N]
  Show recent logs from a Docker container.
  Tries the HTTP API first; falls back to SSH `docker logs` for Compose containers
  (Container Manager 24.x does not support the log API for Compose containers).
"""

import shlex
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get
from lib.ssh import get_client, sudo_run, DOCKER


def get_logs_api(host, sid, name, lines):
    return api_get(host, sid, "SYNO.Docker.Container.Log", "1", "get",
                   name=name, tail=lines)


def get_logs_ssh(name, lines):
    client = get_client()
    try:
        out = sudo_run(client,
            f"{DOCKER} logs --tail={lines} {shlex.quote(name)} 2>&1",
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
        idx = sys.argv.index("--lines")
        try:
            lines = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print(f"--lines requires an integer, got: {sys.argv[idx + 1] if idx + 1 < len(sys.argv) else '(missing)'}")
            sys.exit(1)

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
