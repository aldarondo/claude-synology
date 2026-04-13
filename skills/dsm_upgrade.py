"""
/synology-dsm-upgrade — Trigger a DSM upgrade after checking for available update.
Requires explicit confirmation — this will reboot the NAS.
API: SYNO.Core.Upgrade v1 upgrade
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def trigger_upgrade(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Upgrade",
            "version": "1",
            "method": "upgrade",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        # Check current version and update availability first
        info = api_get(host, sid, "SYNO.Core.System", "1", "info")
        current = info.get("data", {}).get("firmware_ver", "unknown")

        upgrade_check = api_get(host, sid, "SYNO.Core.Upgrade.Server", "4", "check")
        update = upgrade_check.get("data", {}).get("update", {})
        available = update.get("available", False)

        print(f"Current DSM:  {current}")

        if not available:
            print("No DSM update available. System is up to date.")
            return

        new_ver = update.get("version", "unknown")
        print(f"Available:    {new_ver}")
        print()
        print("WARNING: This will download and install the DSM update.")
        print("         The NAS will reboot during the process.")
        print("         All running services will be interrupted.")
        print()

        confirm = input("Type YES to start the DSM upgrade: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

        result = trigger_upgrade(host, sid)
        if result.get("success"):
            print("DSM upgrade initiated. The NAS will reboot when ready.")
        else:
            code = result.get("error", {}).get("code", "?")
            print(f"Upgrade failed (error {code}).")
            print("You can start the upgrade manually via DSM > Control Panel > Update & Restore.")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
