"""
/synology-docker — List all Docker containers: name, image, status, uptime.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def main():
    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Docker.Container", "1", "list",
                       limit=100, offset=0)
        containers = data.get("data", {}).get("containers", [])

        n_running = sum(1 for c in containers if c.get("State", {}).get("Running"))
        n_stopped = len(containers) - n_running

        print(f"=== Docker Containers -- {n_running} running, {n_stopped} stopped ===\n")
        print(f"  {'NAME':<35} {'STATUS':<25} IMAGE")
        print("  " + "-" * 90)

        for c in sorted(containers, key=lambda x: x.get("name", "")):
            name      = c.get("name", "?")
            up_status = c.get("up_status", "")
            image     = c.get("image", "?")
            is_running = c.get("State", {}).get("Running", False)
            health    = c.get("State", {}).get("Health", {}).get("Status", "")
            marker    = "+" if is_running else "-"
            # up_status already includes health info (e.g. "Up 8 days (healthy)")
            status_str = up_status or ("running" if is_running else "stopped")
            print(f"  {marker} {name:<33} {status_str:<25} {image}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
