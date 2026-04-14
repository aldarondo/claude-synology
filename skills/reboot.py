"""
synology reboot
  Gracefully reboot the NAS. Requires YES confirmation.
  The NAS will be unavailable for ~2 minutes during reboot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout
import requests


def main():
    skip_confirm = "--yes" in sys.argv

    if not skip_confirm:
        print("WARNING: This will reboot the NAS. All services will be interrupted.")
        confirm = input("Type YES to confirm reboot: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    host, sid = get_session()
    try:
        resp = requests.post(
            f"{host}/webapi/entry.cgi",
            data={
                "api": "SYNO.Core.System",
                "version": "1",
                "method": "reboot",
                "_sid": sid,
            },
            verify=False,
            timeout=15,
        )
        data = resp.json()
        if data.get("success"):
            print("Reboot initiated. NAS will be unavailable for ~2 minutes.")
        else:
            code = data.get("error", {}).get("code")
            print(f"Error: {data} (code {code})")
    finally:
        try:
            logout(host, sid)
        except Exception:
            pass  # NAS may already be shutting down


if __name__ == "__main__":
    main()
