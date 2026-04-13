"""
/synology-dsm-upgrade — Trigger a DSM upgrade. Requires explicit confirmation.
API: SYNO.Core.Upgrade
WARNING: This reboots the NAS. Always confirm before running.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout
from skills.dsm_check import check_upgrade


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
        data = check_upgrade(host, sid)
        available = data.get("data", {}).get("available", False)
        if not available:
            print("No DSM update available.")
            return
        version = data.get("data", {}).get("version", "unknown")
        confirm = input(f"Upgrade DSM to {version}? This will reboot the NAS. Type YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return
        result = trigger_upgrade(host, sid)
        print(result)
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
