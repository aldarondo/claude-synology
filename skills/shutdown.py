"""
synology shutdown
  Gracefully shut down the NAS. Requires YES confirmation.
  The NAS will power off — you must physically power it back on.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout
import requests


def main():
    skip_confirm = "--yes" in sys.argv

    if not skip_confirm:
        print("WARNING: This will POWER OFF the NAS.")
        print("You will need to physically press the power button to turn it back on.")
        confirm = input("Type YES to confirm shutdown: ")
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
                "method": "shutdown",
                "_sid": sid,
            },
            verify=False,
            timeout=15,
        )
        data = resp.json()
        if data.get("success"):
            print("Shutdown initiated. The NAS will power off shortly.")
        else:
            code = data.get("error", {}).get("code")
            print(f"Error: {data} (code {code})")
    finally:
        try:
            logout(host, sid)
        except Exception:
            pass



if __name__ == "__main__":
    main()
