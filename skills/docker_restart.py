"""
synology docker restart <container-name>
  Restart a single Docker container on the NAS via SSH.
  Requires YES confirmation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, sudo_run, DOCKER


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_restart.py <container-name>")
        sys.exit(1)

    name         = sys.argv[1]
    skip_confirm = "--yes" in sys.argv

    if not skip_confirm:
        confirm = input(f"Restart container '{name}'? Type YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    client = get_client()
    try:
        # Verify the container exists
        out = sudo_run(client,
            f"{DOCKER} ps -a --filter name=^/{name}$ --format '{{{{.Names}}}}' 2>&1")
        if name not in out:
            print(f"Container not found: {name}")
            sys.exit(1)

        print(f"Restarting {name} ...")
        out = sudo_run(client, f"{DOCKER} restart {name} 2>&1", timeout=60)
        print(out or f"{name} restarted")

        # Show new status
        out = sudo_run(client,
            f"{DOCKER} ps --filter name=^/{name}$ --format '{{{{.Names}}}}\t{{{{.Status}}}}' 2>&1")
        if out:
            print(f"\nStatus: {out}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
