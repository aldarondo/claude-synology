"""
/synology-backup-status — Show Hyper Backup task status.
Note: Requires Hyper Backup package to be installed.
Falls back to Config Backup status if Hyper Backup is not present.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get
from datetime import datetime


def fmt_ts(ts):
    if not ts:
        return "never"
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def main():
    host, sid = get_session()
    try:
        # Try Hyper Backup (requires package installed)
        hb = api_get(host, sid, "SYNO.Backup.App.Backup", "1", "list")
        if hb.get("success"):
            tasks = hb.get("data", {}).get("task_list", [])
            print(f"=== Hyper Backup Tasks ({len(tasks)}) ===\n")
            if not tasks:
                print("  No backup tasks configured.")
            for task in tasks:
                name   = task.get("name", "?")
                status = task.get("status", "?")
                last   = fmt_ts(task.get("last_bkup_time"))
                nxt    = fmt_ts(task.get("next_bkup_time"))
                result = task.get("last_bkup_result", "?")
                print(f"  Task:      {name}")
                print(f"  Status:    {status}")
                print(f"  Last run:  {last}  →  Result: {result}")
                print(f"  Next run:  {nxt}")
                print()
            return

        # Fallback: Config backup status
        cfg_bkp = api_get(host, sid, "SYNO.Backup.Config.Backup", "2", "get")
        if cfg_bkp.get("success"):
            print("=== Config Backup Status ===\n")
            import json
            print(json.dumps(cfg_bkp.get("data", {}), indent=2))
        else:
            code = hb.get("error", {}).get("code", "?")
            print(f"Backup status unavailable (error {code}).")
            print("Ensure Hyper Backup is installed via Package Center.")

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
