"""
/synology-install-package <package-id> — Install a package from Package Center.
API: SYNO.Core.Package.Installation v1

Note: The DSM Package Installation API requires a download URL or the package to
be pre-staged. Searching and installing from Package Center requires a MyDS account
session that is separate from the admin session. This skill handles what's possible
via the HTTP API; complex installs are better done via DSM > Package Center UI.

Usage:
  install_package.py <id>                Install by package ID (if already downloaded)
  install_package.py <id> <volume>       Install to specific volume (e.g. /volume1)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def install(host, sid, package_id, volume="/volume1"):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package.Installation",
            "version": "1",
            "method": "install",
            "id": package_id,
            "volume_path": volume,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: install_package.py <package-id> [volume]")
        print("       volume defaults to /volume1")
        print()
        print("Note: Package IDs can be found in DSM > Package Center.")
        print("      Full browser-based install is more reliable for new packages.")
        sys.exit(1)

    package_id = sys.argv[1]
    volume = sys.argv[2] if len(sys.argv) > 2 else "/volume1"

    confirm = input(f"Install '{package_id}' to {volume}? Type YES to confirm: ")
    if confirm.strip() != "YES":
        print("Aborted.")
        return

    host, sid = get_session()
    try:
        result = install(host, sid, package_id, volume)
        if result.get("success"):
            print(f"Install started: {package_id}")
            print("Monitor progress in DSM > Package Center.")
        else:
            code = result.get("error", {}).get("code", "?")
            if code == 120:
                print(f"Package '{package_id}' not found or not available for download via API.")
                print("Install it manually via DSM > Package Center.")
            else:
                print(f"Install failed (error {code}).")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
