"""
/synology-status — System dashboard: CPU, RAM, temps, uptime, disk usage.
API: SYNO.Core.System, SYNO.Core.System.Utilization
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def get_utilization(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.System.Utilization",
            "version": "1",
            "method": "get",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def get_system_info(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.System",
            "version": "1",
            "method": "info",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        util = get_utilization(host, sid)
        info = get_system_info(host, sid)
        # TODO: parse and print formatted dashboard
        print("=== Synology Status ===")
        print("(raw responses below — formatting TODO)")
        import json
        print(json.dumps(util.get("data", {}), indent=2))
        print(json.dumps(info.get("data", {}), indent=2))
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
