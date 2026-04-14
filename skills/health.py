"""
synology health
  Single-command health check. Aggregates storage, temps, RAID, containers,
  and DSM update status. Flags anything that needs attention.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, api_get, logout

# Thresholds
VOLUME_WARN_PCT  = 85
TEMP_CPU_WARN    = 70   # °C
TEMP_DISK_WARN   = 50   # °C


def _bar(pct, width=20):
    filled = int(width * pct / 100)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {pct:.0f}%"


def main():
    host, sid = get_session()
    warnings = []

    try:
        print("=== NAS Health Check ===\n")

        # ── Storage ───────────────────────────────────────────────────────────
        storage = api_get(host, sid, "SYNO.Storage.CGI.Storage", 1, "load_info")
        if storage.get("success"):
            d = storage["data"]

            print("Storage:")
            for vol in d.get("volumes", []):
                name  = vol.get("display_name") or vol.get("vol_path", "?")
                total = int(vol.get("size", {}).get("total", 0) or 0)
                used  = int(vol.get("size", {}).get("used",  0) or 0)
                pct   = round(used / total * 100, 1) if total else 0
                status = vol.get("status", "?")
                flag = " !!" if pct >= VOLUME_WARN_PCT else ""
                print(f"  {name:<12} {_bar(pct)}{flag}  [{status}]")
                if pct >= VOLUME_WARN_PCT:
                    warnings.append(f"Volume {name} is {pct}% full")
                if status not in ("normal",):
                    warnings.append(f"Volume {name} status: {status}")

            for pool in d.get("storagePools", []):
                name   = pool.get("pool_path") or pool.get("name") or "pool"
                status = pool.get("status", "?")
                desc   = pool.get("desc", "")
                flag = " !!" if status != "normal" else ""
                print(f"  {name:<12} {desc:<18} [{status}]{flag}")
                if status != "normal":
                    warnings.append(f"RAID pool {name} status: {status}")

        # ── Disk Temperatures & SMART ─────────────────────────────────────────
        print("\nDisk Health:")
        storage = api_get(host, sid, "SYNO.Storage.CGI.Storage", 1, "load_info")
        if storage.get("success"):
            for disk in storage["data"].get("disks", []):
                if disk.get("diskType") not in ("SATA", "SAS", "NVMe", "DISK"):
                    continue
                name  = disk.get("name", "?")
                temp  = disk.get("temp", 0) or 0
                smart = disk.get("smart_status", "normal")
                flag  = ""
                if temp >= TEMP_DISK_WARN:
                    flag = " !!"
                    warnings.append(f"Disk {name} temperature high: {temp}C")
                if smart != "normal":
                    flag = " !!"
                    warnings.append(f"Disk {name} SMART: {smart}")
                print(f"  {name:<12} {temp}C  SMART: {smart}{flag}")

        # ── Containers ────────────────────────────────────────────────────────
        print("\nContainers:")
        containers = api_get(host, sid, "SYNO.Docker.Container", 1, "list",
                             limit=100, offset=0)
        if containers.get("success"):
            items = containers["data"].get("containers", [])
            if not items:
                print("  (none)")
            for c in sorted(items, key=lambda x: x.get("name", "")):
                name   = c.get("name", "?")
                status = c.get("status", "?")
                if status == "running":
                    print(f"  + {name:<35} running")
                else:
                    print(f"  - {name:<35} {status} !!")
                    warnings.append(f"Container {name} is {status}")

        # ── DSM update ────────────────────────────────────────────────────────
        print("\nDSM Update:")
        upgrade = api_get(host, sid, "SYNO.Core.Upgrade.Server", 4, "check")
        if upgrade.get("success"):
            avail = upgrade["data"].get("available", False)
            if avail:
                ver = upgrade["data"].get("version", "unknown")
                print(f"  Update available: {ver} !!")
                warnings.append(f"DSM update available: {ver}")
            else:
                print("  Up to date")
        else:
            print("  (could not check)")

        # ── Summary ───────────────────────────────────────────────────────────
        print(f"\n{'=' * 44}")
        if warnings:
            print(f"  {len(warnings)} WARNING(S):")
            for w in warnings:
                print(f"    !! {w}")
        else:
            print("  All systems OK")
        print(f"{'=' * 44}")

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
