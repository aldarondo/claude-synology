"""
/synology-storage — Volume health, RAID status, disk S.M.A.R.T summary.
API: SYNO.Storage.CGI.Storage, SYNO.Core.Storage.Volume
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def get_volumes(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Storage.Volume",
            "version": "1",
            "method": "list",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def get_disks(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Storage.Disk",
            "version": "1",
            "method": "list",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        volumes = get_volumes(host, sid)
        disks = get_disks(host, sid)
        print("=== Volumes ===")
        import json
        print(json.dumps(volumes.get("data", {}), indent=2))
        print("\n=== Disks ===")
        print(json.dumps(disks.get("data", {}), indent=2))
        # TODO: format as readable table with health status, capacity used/total
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
