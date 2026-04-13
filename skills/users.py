"""
/synology-users — List users and group memberships.
API: SYNO.Core.User, SYNO.Core.Group
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def list_users(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.User",
            "version": "1",
            "method": "list",
            "additional": '["email","description","groups"]',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def list_groups(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Core.Group",
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
        users = list_users(host, sid)
        groups = list_groups(host, sid)
        user_list = users.get("data", {}).get("users", [])
        group_list = groups.get("data", {}).get("groups", [])

        print(f"=== Users ({len(user_list)}) ===\n")
        for u in sorted(user_list, key=lambda x: x.get("name", "")):
            name = u.get("name", "?")
            email = u.get("email", "")
            grps = ", ".join(u.get("groups", []))
            print(f"  {name:<25} {email:<35} groups: {grps}")

        print(f"\n=== Groups ({len(group_list)}) ===\n")
        for g in sorted(group_list, key=lambda x: x.get("name", "")):
            print(f"  {g.get('name', '?')}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
