"""
/synology-logs [--severity error|warning|info] [--lines N] — View system and security logs.
API: SYNO.Core.Log.Viewer
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


SEVERITY_MAP = {"error": 3, "warning": 2, "info": 1}


def get_logs(host, sid, severity=None, lines=50):
    params = {
        "api": "SYNO.Core.Log.Viewer",
        "version": "1",
        "method": "list",
        "limit": lines,
        "_sid": sid,
    }
    if severity and severity in SEVERITY_MAP:
        params["level"] = SEVERITY_MAP[severity]
    resp = requests.get(f"{host}/webapi/entry.cgi", params=params, verify=False)
    return resp.json()


def main():
    severity = None
    lines = 50
    if "--severity" in sys.argv:
        idx = sys.argv.index("--severity")
        severity = sys.argv[idx + 1]
    if "--lines" in sys.argv:
        idx = sys.argv.index("--lines")
        lines = int(sys.argv[idx + 1])

    host, sid = get_session()
    try:
        data = get_logs(host, sid, severity, lines)
        entries = data.get("data", {}).get("items", [])
        label = f"severity={severity}" if severity else "all"
        print(f"=== System Logs ({label}, last {lines}) ===\n")
        for entry in entries:
            time = entry.get("time", "")
            level = entry.get("level", "")
            msg = entry.get("description", "")
            print(f"  [{time}] [{level}] {msg}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
