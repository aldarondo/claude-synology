"""
synology install <package-name>
  Search the Package Center catalog and install a package by name.

Usage:
  install_package.py <name>           Search catalog and install
  install_package.py <name> --search  Search only, don't install

How it works:
  1. Queries SYNO.Core.Package.Server (v1) to browse the catalog (no MyDS needed)
  2. Finds the best match by package name
  3. Installs via SYNO.Core.Package.Installation using pkgname (not id)

Note: Premium packages and hardware-specific packages still require the DSM UI.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout, api_get


def search_catalog(host, sid, query, limit=50):
    """Search Package Center catalog. Returns list of matching package dicts."""
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api":    "SYNO.Core.Package.Server",
            "version": "1",
            "method": "list",
            "limit":  limit,
            "offset": 0,
            "_sid":   sid,
        },
        verify=False,
        timeout=30,
    )
    data = resp.json()
    if not data.get("success"):
        return [], data.get("error", {}).get("code")

    # Response: {"data": {"data": [...packages...], "total": N}}
    packages = data.get("data", {}).get("data", [])
    q = query.lower()
    matches = [
        p for p in packages
        if q in p.get("package", "").lower() or q in p.get("dname", "").lower()
    ]
    return matches, None


def install_package(host, sid, pkgname, volume="/volume1"):
    resp = requests.post(
        f"{host}/webapi/entry.cgi",
        data={
            "api":         "SYNO.Core.Package.Installation",
            "version":     "1",
            "method":      "install",
            "pkgname":     pkgname,
            "volume_path": volume,
            "_sid":        sid,
        },
        verify=False,
        timeout=60,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: install_package.py <package-name> [--search] [--volume /volumeN]")
        sys.exit(1)

    args        = sys.argv[1:]
    search_only = "--search" in args
    args        = [a for a in args if a != "--search"]

    volume = "/volume1"
    if "--volume" in args:
        idx    = args.index("--volume")
        volume = args[idx + 1]
        args   = [a for a in args if a not in ("--volume", volume)]

    query = args[0]

    host, sid = get_session()
    try:
        print(f"Searching Package Center for '{query}' ...")
        matches, err_code = search_catalog(host, sid, query)

        if err_code is not None:
            print(f"Catalog search failed (error {err_code}).")
            print("Install manually via DSM > Package Center.")
            return

        if not matches:
            print(f"No packages found matching '{query}'.")
            print("Try a shorter search term, or install via DSM > Package Center.")
            return

        print(f"\nFound {len(matches)} match(es):\n")
        for i, pkg in enumerate(matches):
            name    = pkg.get("package", "?")
            dname   = pkg.get("dname", name)
            version = pkg.get("version", "?")
            desc    = pkg.get("desc", "")[:60]
            print(f"  [{i+1}] {dname} ({name})  v{version}")
            if desc:
                print(f"      {desc}")

        if search_only:
            return

        if len(matches) == 1:
            chosen = matches[0]
        else:
            print()
            choice = input(f"Enter number to install (1-{len(matches)}) or q to quit: ").strip()
            if choice.lower() == "q":
                print("Aborted.")
                return
            try:
                chosen = matches[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid selection.")
                return

        pkgname = chosen.get("package", "")
        dname   = chosen.get("dname", pkgname)
        print(f"\nInstall '{dname}' ({pkgname}) to {volume}?")
        confirm = input("Type YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

        result = install_package(host, sid, pkgname, volume)
        if result.get("success"):
            print(f"Install started: {dname}")
            print("Monitor progress in DSM > Package Center.")
        else:
            code = result.get("error", {}).get("code", "?")
            if code == 120:
                print(f"Package not available for automated install (error 120).")
                print("This package may require the DSM UI or a MyDS account.")
            else:
                print(f"Install failed (error {code}).")
                print("Try installing via DSM > Package Center.")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
