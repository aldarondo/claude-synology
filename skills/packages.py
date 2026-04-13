"""
/synology-packages — List all installed packages with version and type.
Usage: python skills/packages.py [--filter <text>]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def main():
    filter_text = None
    if "--filter" in sys.argv:
        idx = sys.argv.index("--filter")
        filter_text = sys.argv[idx + 1].lower()

    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Core.Package", "1", "list",
                       additional='["install_type"]')
        packages = data.get("data", {}).get("packages", [])

        if filter_text:
            packages = [p for p in packages if filter_text in p.get("name", "").lower()
                        or filter_text in p.get("id", "").lower()]

        packages = sorted(packages, key=lambda p: p.get("name", "").lower())

        print(f"=== Installed Packages ({len(packages)}) ===\n")
        print(f"  {'NAME':<40} {'VERSION':<25} TYPE")
        print("  " + "-" * 75)
        for pkg in packages:
            name    = pkg.get("name", "?")
            version = pkg.get("version", "?")
            itype   = pkg.get("additional", {}).get("install_type", "") or "user"
            print(f"  {name:<40} {version:<25} {itype}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
