"""
/synology-logs [--level error|warning|info] [--lines N] [--type system|connection|file]
View DSM system logs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get

LEVEL_COLORS = {"err": "!!", "warning": "! ", "info": "  "}


def main():
    level = None
    lines = 50
    logtype = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--level" and i + 1 < len(args):
            level = args[i + 1]; i += 2
        elif args[i] == "--lines" and i + 1 < len(args):
            try:
                lines = int(args[i + 1])
            except ValueError:
                print(f"--lines requires an integer, got: {args[i + 1]}")
                sys.exit(1)
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            logtype = args[i + 1]; i += 2
        else:
            i += 1

    host, sid = get_session()
    try:
        params = dict(limit=lines, offset=0)
        if level:
            params["level"] = level
        if logtype:
            params["logtype"] = logtype

        data = api_get(host, sid, "SYNO.Core.SyslogClient.Log", "1", "list", **params)
        items      = data.get("data", {}).get("items", [])
        err_count  = data.get("data", {}).get("errorCount", 0)
        info_count = data.get("data", {}).get("infoCount", 0)

        label = f"level={level}" if level else "all levels"
        print(f"=== System Logs ({label}, last {lines}) — {err_count} errors, {info_count} info ===\n")
        print(f"  {'TIME':<22} {'LEVEL':<10} {'TYPE':<12} {'USER':<12} MESSAGE")
        print("  " + "-" * 95)

        for entry in items:
            time  = entry.get("time", "?")
            lvl   = entry.get("level", "?")
            ltype = entry.get("logtype", "?")
            who   = entry.get("who", "?")
            descr = entry.get("descr", "?")
            marker = LEVEL_COLORS.get(lvl, "·")
            print(f"  {marker} {time:<21} {lvl:<10} {ltype:<12} {who:<12} {descr}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
