"""
/synology-upgrade-package [<package-id>] — Upgrade a package or list upgradeable packages.
API: SYNO.Core.Package.Installation v1

Usage:
  upgrade_package.py              Check which packages have updates available
  upgrade_package.py <id>         Upgrade a specific package (e.g. Jellyfin)
  upgrade_package.py <id> --yes   Skip confirmation

Error 4501 = package is already at the latest version.
Package IDs come from the 'id' column in: python skills/packages.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


ERROR_MSGS = {
    4501: "already at the latest version (no update available)",
    120:  "package not found — check the ID with: python skills/packages.py",
}


def upgrade(host, sid, package_id):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package.Installation",
            "version": "1",
            "method": "upgrade",
            "id": package_id,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    skip_confirm = "--yes" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--yes"]
    package_id = args[0] if args else None

    host, sid = get_session()
    try:
        if not package_id:
            # List all installed packages — user can cross-reference for upgrade candidates
            data = api_get(host, sid, "SYNO.Core.Package", "1", "list",
                           additional='["install_type"]')
            packages = data.get("data", {}).get("packages", [])
            user_pkgs = [p for p in packages
                         if p.get("additional", {}).get("install_type", "") != "system"]
            print(f"=== User-installed packages ({len(user_pkgs)}) ===\n")
            print(f"  {'ID':<30} {'NAME':<35} VERSION")
            print("  " + "-" * 80)
            for p in sorted(user_pkgs, key=lambda x: x.get("name", "").lower()):
                print(f"  {p.get('id','?'):<30} {p.get('name','?'):<35} {p.get('version','?')}")
            print("\nTo upgrade: python skills/upgrade_package.py <id>")
            return

        if not skip_confirm:
            confirm = input(f"Upgrade package '{package_id}'? Type YES to confirm: ")
            if confirm.strip() != "YES":
                print("Aborted.")
                return

        result = upgrade(host, sid, package_id)
        if result.get("success"):
            print(f"Upgrade started: {package_id}")
            print("Monitor progress in DSM > Package Center.")
        else:
            code = result.get("error", {}).get("code", "?")
            msg = ERROR_MSGS.get(code, f"error {code}")
            print(f"Upgrade failed: {msg}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
