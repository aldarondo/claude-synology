"""
/synology-storage — Volume usage, storage pool status, and disk health summary.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def to_tb(b):
    b = int(b) if b else 0
    return f"{b / 1024 ** 4:.2f} TB"


def to_gb(b):
    b = int(b) if b else 0
    return f"{b / 1024 ** 3:.1f} GB"


def pct(used, total):
    used, total = int(used or 0), int(total or 1)
    return round(used / total * 100)


def bar(p, width=20):
    filled = int(p / 100 * width)
    return "[" + "#" * filled + "." * (width - filled) + f"] {p}%"


def main():
    host, sid = get_session()
    try:
        data = api_get(host, sid, "SYNO.Storage.CGI.Storage", "1", "load_info")
        d = data.get("data", {})

        volumes = d.get("volumes", [])
        disks   = d.get("disks", [])
        pools   = d.get("storagePools", [])

        # ── Volumes ────────────────────────────────────────────
        print(f"\n=== Volumes ({len(volumes)}) ===\n")
        for v in volumes:
            vid    = v.get("id", "?")
            desc   = v.get("desc", "")
            status = v.get("status", "?")
            size   = v.get("size", {})
            total  = size.get("total", 0)
            used   = size.get("used", 0)
            p      = pct(used, total) if total else 0
            marker = "OK" if status == "normal" else "!!"
            print(f"  {marker} {vid:<12} {desc}")
            print(f"    Used:    {to_tb(used)} / {to_tb(total)}  {bar(p)}")
            print(f"    Status:  {status}")
            print()

        # ── Storage Pools ──────────────────────────────────────
        if pools:
            print(f"=== Storage Pools ({len(pools)}) ===\n")
            print(f"  {'ID':<15} {'TYPE':<22} {'RAW CAPACITY':<15} STATUS")
            print("  " + "-" * 60)
            for p in pools:
                pid    = p.get("id", "?")
                desc   = p.get("desc", "")
                status = p.get("status", "?")
                size   = p.get("size", {})
                total  = size.get("total", 0)
                marker = "OK" if status == "normal" else "!!"
                print(f"  {marker} {pid:<13} {desc:<22} {to_tb(total):<15} {status}")
            print()

        # ── Disks ──────────────────────────────────────────────
        internal = [d for d in disks if d.get("container") != "ebox"]
        external = [d for d in disks if d.get("container") == "ebox"]

        print(f"=== Internal Disks ({len(internal)}) ===\n")
        print(f"  {'SLOT':<8} {'MODEL':<30} {'SIZE':<12} {'TEMP':<8} {'SMART':<10} STATUS")
        print("  " + "-" * 80)
        for disk in sorted(internal, key=lambda x: x.get("order", 0)):
            slot   = disk.get("name", disk.get("id", "?"))
            model  = disk.get("model", "?")
            size   = to_tb(disk.get("size_total", 0))
            temp   = f"{disk.get('temp', '?')}C"
            smart  = disk.get("smart_status", "?")
            status = disk.get("status", "?")
            marker = "OK" if status == "normal" else "!!"
            print(f"  {marker} {slot:<6} {model:<30} {size:<12} {temp:<8} {smart:<10} {status}")

        if external:
            print(f"\n=== Expansion Unit Disks ({len(external)}) ===\n")
            for disk in sorted(external, key=lambda x: x.get("order", 0)):
                slot   = disk.get("name", disk.get("id", "?"))
                model  = disk.get("model", "?")
                size   = to_tb(disk.get("size_total", 0))
                temp   = f"{disk.get('temp', '?')}C"
                status = disk.get("status", "?")
                marker = "OK" if status == "normal" else "!!"
                print(f"  {marker} {slot:<10} {model:<30} {size:<12} {temp:<8} {status}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
