"""
/synology-docker-compose <path> <action> — Run docker compose commands on the NAS via SSH.

Actions: up, down, pull, logs, ps, restart
Path: directory on the NAS containing docker-compose.yml

Usage:
  docker_compose.py /volume1/docker/brian-mcp up
  docker_compose.py /volume1/docker/brian-mcp logs
  docker_compose.py /volume1/docker/brian-mcp ps
  docker_compose.py /volume1/docker/brian-mcp pull
  docker_compose.py /volume1/docker/brian-mcp down      (requires YES)
  docker_compose.py /volume1/docker/brian-mcp restart   (requires YES)
"""

import shlex
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, sudo_run, DOCKER

DESTRUCTIVE = {"down", "restart"}
LOG_LINES   = 50


def main():
    if len(sys.argv) < 3:
        print("Usage: docker_compose.py <nas-path> <action> [--yes]")
        print("Actions: up, down, pull, logs, ps, restart")
        sys.exit(1)

    path         = sys.argv[1]
    action       = sys.argv[2].lower()
    skip_confirm = "--yes" in sys.argv
    safe_path    = shlex.quote(path)

    if action in DESTRUCTIVE and not skip_confirm:
        confirm = input(f"Run 'docker compose {action}' in {path}? Type YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    client = get_client()
    try:
        # Verify the path exists
        out = sudo_run(client, f"test -d {safe_path} && echo EXISTS || echo MISSING")
        if "MISSING" in out:
            print(f"Directory not found on NAS: {path}")
            sys.exit(1)

        # Verify compose file exists
        out = sudo_run(client,
            f"test -f {safe_path}/docker-compose.yml -o -f {safe_path}/compose.yml && echo OK || echo MISSING")
        if "MISSING" in out:
            print(f"No docker-compose.yml found in {path}")
            sys.exit(1)

        # Build and run the command
        if action == "up":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose up -d'"
        elif action == "down":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose down'"
        elif action == "pull":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose pull'"
        elif action == "logs":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose logs --tail={LOG_LINES}'"
        elif action == "ps":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose ps'"
        elif action == "restart":
            cmd = f"sh -c 'cd {safe_path} && {DOCKER} compose restart'"
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)

        print(f"$ sudo {cmd}\n")
        out = sudo_run(client, cmd, timeout=120)
        print(out)

    finally:
        client.close()


if __name__ == "__main__":
    main()
