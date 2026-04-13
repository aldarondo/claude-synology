"""
/synology-users — List all NAS users with email and group memberships.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def main():
    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Core.User", "1", "list",
                       additional='["email","description","groups"]',
                       offset=0, limit=200)
        users = data.get("data", {}).get("users", [])

        print(f"=== NAS Users ({len(users)}) ===\n")
        print(f"  {'NAME':<20} {'EMAIL':<30} {'DESCRIPTION':<25} GROUPS")
        print("  " + "-" * 90)

        for u in sorted(users, key=lambda x: x.get("name", "").lower()):
            name  = u.get("name", "?")
            email = u.get("email", "")
            desc  = u.get("description", "")
            grps  = ", ".join(u.get("groups", [])) or "-"
            print(f"  {name:<20} {email:<30} {desc:<25} {grps}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
