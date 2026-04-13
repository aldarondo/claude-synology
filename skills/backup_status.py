"""
/synology-backup-status — Hyper Backup job status: last run, next run, result.
API: SYNO.Backup.Task
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout
from datetime import datetime


def list_backup_tasks(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Backup.Task",
            "version": "1",
            "method": "list",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def format_ts(ts):
    if not ts:
        return "never"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def main():
    host, sid = get_session()
    try:
        data = list_backup_tasks(host, sid)
        tasks = data.get("data", {}).get("task_list", [])
        print(f"=== Hyper Backup Tasks ({len(tasks)}) ===\n")
        for task in tasks:
            name = task.get("name", "?")
            status = task.get("status", "?")
            last_bkup = format_ts(task.get("last_bkup_time"))
            next_bkup = format_ts(task.get("next_bkup_time"))
            result = task.get("last_bkup_result", "?")
            print(f"  Task:       {name}")
            print(f"  Status:     {status}")
            print(f"  Last run:   {last_bkup}  Result: {result}")
            print(f"  Next run:   {next_bkup}")
            print()
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
