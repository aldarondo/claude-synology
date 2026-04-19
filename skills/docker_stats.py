"""
/synology docker stats
  Snapshot CPU, memory, and I/O for all running containers (non-streaming).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, sudo_run, DOCKER


def main():
    client = get_client()
    try:
        fmt = r"table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
        out = sudo_run(
            client,
            f"{DOCKER} stats --no-stream --format '{fmt}'",
            timeout=20,
        )
        print(out or "No running containers.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
