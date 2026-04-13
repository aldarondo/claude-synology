"""
/synology-dsm-check — Show current DSM version and check for available updates.
Uses SYNO.Core.Upgrade.Server to query the update server.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def main():
    host, sid = get_session()
    try:
        # Current version from system info
        info = api_get(host, sid, "SYNO.Core.System", "1", "info")
        i = info.get("data", {})

        print("=== DSM Version Info ===\n")
        print(f"  Installed:  {i.get('firmware_ver', '?')}")
        print(f"  Model:      {i.get('model', '?')}")
        print(f"  Firmware:   {i.get('firmware_date', '?')}")

        # Check update server
        upgrade = api_get(host, sid, "SYNO.Core.Upgrade.Server", "4", "check")
        if upgrade.get("success"):
            update = upgrade.get("data", {}).get("update", {})
            available = update.get("available", False)
            if available:
                new_ver = update.get("version", "unknown")
                print(f"\n  !!  Update available: {new_ver}")
                notes = update.get("release_notes_url") or update.get("releaseNote", "")
                if notes:
                    print(f"      Release notes: {notes}")
            else:
                print(f"\n  OK  DSM is up to date.")
        else:
            code = upgrade.get("error", {}).get("code", "?")
            print(f"\n  Update check failed (error {code}).")

        # Auto-upgrade settings
        setting = api_get(host, sid, "SYNO.Core.Upgrade.Setting", "4", "get")
        if setting.get("success"):
            sd = setting.get("data", {})
            auto = sd.get("auto_upgrade_type", "disabled")
            print(f"\n  Auto-upgrade: {auto}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
