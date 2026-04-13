"""
/synology-upgrade-package [package-name|--all] — Upgrade a specific package or all outdated ones.
API: SYNO.Core.Package
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def upgrade_package(host, sid, package_id):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package",
            "version": "2",
            "method": "upgrade",
            "id": f'"{package_id}"',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if not target:
        print("Usage: upgrade_package.py <package-id|--all>")
        sys.exit(1)

    host, sid = get_session()
    try:
        if target == "--all":
            # TODO: list outdated packages then upgrade each
            print("--all not yet implemented")
        else:
            result = upgrade_package(host, sid, target)
            print(result)
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
