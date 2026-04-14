"""
synology docker pull [<image:tag>]
  List local Docker images, or pull a new/updated image via SSH.

Usage:
  docker_pull.py               List all local images with upgradable flag
  docker_pull.py <image:tag>   Pull image via SSH (requires YES confirmation)

Note: SYNO.Docker.Image pull was removed in Container Manager 24.x.
Pull is handled via SSH `docker pull` instead.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get
from lib.ssh import get_client, sudo_run, DOCKER


def main():
    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Docker.Image", "1", "list", limit=100, offset=0)
        if not data.get("success"):
            code = data.get("error", {}).get("code", "?")
            print(f"Could not list images (error {code}).")
            return

        images    = data.get("data", {}).get("images", [])
        upgradable = [img for img in images if img.get("upgradable")]

        print(f"=== Local Docker Images ({len(images)}) ===\n")
        print(f"  {'REPOSITORY':<40} {'TAG':<20} {'SIZE':>8}  UPGRADABLE")
        print("  " + "-" * 80)
        for img in sorted(images, key=lambda x: x.get("repository", "")):
            repo     = img.get("repository", "?")
            tags     = ", ".join(img.get("tags", [])) or "?"
            size     = img.get("size", 0)
            size_str = f"{size / 1024 ** 2:.0f} MB" if size else "?"
            upg      = "  YES" if img.get("upgradable") else ""
            print(f"  {repo:<40} {tags:<20} {size_str:>8}{upg}")

        if upgradable:
            print(f"\n  {len(upgradable)} image(s) have updates available.")

    finally:
        logout(host, sid)

    # Pull via SSH if image specified
    if len(sys.argv) > 1:
        image = sys.argv[1]
        skip_confirm = "--yes" in sys.argv
        print()
        if not skip_confirm:
            confirm = input(f"Pull '{image}' on the NAS? Type YES to confirm: ")
            if confirm.strip() != "YES":
                print("Aborted.")
                return

        client = get_client()
        try:
            print(f"Pulling {image} ...")
            out = sudo_run(client, f"{DOCKER} pull {image} 2>&1", timeout=300)
            print(out or "Done.")
        finally:
            client.close()


if __name__ == "__main__":
    main()
