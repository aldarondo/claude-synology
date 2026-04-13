"""
/synology-dsm-check — Show current DSM version and available update info.
API: SYNO.Core.Upgrade
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def check_upgrade(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Upgrade",
            "version": "1",
            "method": "check",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        data = check_upgrade(host, sid)
        info = data.get("data", {})
        print("=== DSM Update Check ===")
        # TODO: format current version, available version, release notes URL
        import json
        print(json.dumps(info, indent=2))
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
