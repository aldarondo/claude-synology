"""
/synology-packages — List installed packages, flag outdated ones.
API: SYNO.Core.Package
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def list_packages(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package",
            "version": "2",
            "method": "list",
            "additional": '["description","description_enu","dependent_packages","beta","distributor","distributor_url","maintainer","maintainer_url","dsm_apps","ds_app","report_beta_url","support_center","startable","installed_info","install_type","autoupdate","silent_upgrade"]',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        data = list_packages(host, sid)
        packages = data.get("data", {}).get("packages", [])
        print(f"=== Installed Packages ({len(packages)}) ===\n")
        # TODO: flag outdated, format table
        for pkg in sorted(packages, key=lambda p: p.get("name", "")):
            name = pkg.get("name", "?")
            version = pkg.get("version", "?")
            status = pkg.get("status", "?")
            print(f"  {name:<40} {version:<20} {status}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
