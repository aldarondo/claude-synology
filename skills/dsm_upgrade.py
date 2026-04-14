"""
synology dsm upgrade — Check for and trigger a DSM upgrade via SSH synoupgrade CLI.

Steps:
  1. Check current version and update availability (HTTP API)
  2. If update available: prompt YES confirmation
  3. SSH: sudo synoupgrade --download
  4. SSH: sudo synoupgrade --start  (triggers install + reboot)

Note: SYNO.Core.Upgrade upgrade (HTTP API) returns error 103 in DSM 7.2+.
This skill uses the official Synology CLI tool `synoupgrade` via SSH instead,
as documented in the Synology CLI Administrator Guide.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get
from lib.ssh import get_client, sudo_run


def main():
    host, sid = get_session()
    try:
        info  = api_get(host, sid, "SYNO.Core.System", "1", "info")
        current = info.get("data", {}).get("firmware_ver", "unknown")

        check = api_get(host, sid, "SYNO.Core.Upgrade.Server", "4", "check")
        available = check.get("data", {}).get("available", False)

        print(f"Current DSM:  {current}")

        if not available:
            print("No update available. System is up to date.")
            return

        new_ver = check.get("data", {}).get("version", "unknown")
        print(f"Available:    {new_ver}")
        print()
        print("WARNING: This will download and install the DSM update.")
        print("         The NAS will REBOOT during the process.")
        print("         All running services will be interrupted.")
        print()

        confirm = input("Type YES to start the DSM upgrade: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    finally:
        logout(host, sid)

    client = get_client()
    try:
        # Verify synoupgrade is available
        out = sudo_run(client, "which synoupgrade 2>&1 || echo NOT_FOUND")
        if "NOT_FOUND" in out or not out.strip():
            print("Error: synoupgrade CLI not found on NAS.")
            print("Upgrade manually via DSM > Control Panel > Update & Restore.")
            sys.exit(1)

        # Double-check via CLI
        print("Verifying update via synoupgrade ...")
        out = sudo_run(client, "synoupgrade --check 2>&1", timeout=30)
        print(out)

        # Download
        print("\nDownloading update ...")
        out = sudo_run(client, "synoupgrade --download 2>&1", timeout=300)
        print(out)

        if "error" in out.lower() or "fail" in out.lower():
            print("\nDownload may have failed — check output above.")
            confirm2 = input("Continue with install anyway? Type YES to confirm: ")
            if confirm2.strip() != "YES":
                print("Aborted.")
                return

        # Install (triggers reboot)
        print("\nStarting upgrade. The NAS will reboot — connection will drop.")
        out = sudo_run(client, "synoupgrade --start 2>&1", timeout=60)
        print(out or "Upgrade initiated.")

    finally:
        client.close()


if __name__ == "__main__":
    main()
