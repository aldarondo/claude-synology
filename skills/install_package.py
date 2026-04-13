"""
/synology-install-package <package-name> — Search Package Center and install a package.
API: SYNO.Core.Package.Server, SYNO.Core.Package
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def search_packages(host, sid, query):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package.Server",
            "version": "2",
            "method": "find",
            "name": query,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def install_package(host, sid, package_id):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Package",
            "version": "2",
            "method": "install",
            "id": f'"{package_id}"',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: install_package.py <package-name>")
        sys.exit(1)
    query = sys.argv[1]
    host, sid = get_session()
    try:
        results = search_packages(host, sid, query)
        # TODO: display results, prompt selection, confirm install
        import json
        print(json.dumps(results.get("data", {}), indent=2))
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
