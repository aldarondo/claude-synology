"""
/synology-docker-pull [<image:tag>] — List local Docker images or pull a new image.
API: SYNO.Docker.Image v1

Usage:
  docker_pull.py               List all local images (with upgradable flag)
  docker_pull.py <image:tag>   Pull is not yet supported via the HTTP API —
                               prints instructions for pulling via DSM UI.

Note: The SYNO.Docker.Image pull method is not exposed in Container Manager 24.x
HTTP API. See ROADMAP for the Cowork research task tracking this.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from lib.auth import get_session, logout, api_get


def main():
    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Docker.Image", "1", "list", limit=100, offset=0)
        if not data.get("success"):
            code = data.get("error", {}).get("code", "?")
            print(f"Could not list images (error {code}).")
            return

        images = data.get("data", {}).get("images", [])
        upgradable = [img for img in images if img.get("upgradable")]

        print(f"=== Local Docker Images ({len(images)}) ===\n")
        print(f"  {'REPOSITORY':<40} {'TAGS':<20} {'SIZE':>8}  UPGRADABLE")
        print("  " + "-" * 80)

        for img in sorted(images, key=lambda x: x.get("repository", "")):
            repo  = img.get("repository", "?")
            tags  = ", ".join(img.get("tags", [])) or "?"
            size  = img.get("size", 0)
            size_str = f"{size / 1024 ** 2:.0f} MB" if size else "?"
            upg   = "  YES" if img.get("upgradable") else ""
            print(f"  {repo:<40} {tags:<20} {size_str:>8}{upg}")

        if upgradable:
            print(f"\n  {len(upgradable)} image(s) have updates available.")

        if len(sys.argv) > 1:
            image_arg = sys.argv[1]
            print(f"\nPull '{image_arg}' is not yet available via the HTTP API.")
            print("To pull an image, open DSM and go to:")
            print("  Container Manager > Image > Add > Add from URL")
            print(f"  Enter: {image_arg}")

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
