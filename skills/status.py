"""
/synology-status — System dashboard: model, DSM version, CPU, RAM, temps, network, disk I/O.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.auth import get_session, logout, api_get


def bytes_per_sec(b):
    if b >= 1024 ** 2:
        return f"{b / 1024 ** 2:.1f} MB/s"
    if b >= 1024:
        return f"{b / 1024:.1f} KB/s"
    return f"{b} B/s"


def main():
    host, sid = get_session()
    try:
        util = api_get(host, sid, "SYNO.Core.System.Utilization", "1", "get")
        info = api_get(host, sid, "SYNO.Core.System", "1", "info")

        u = util.get("data", {})
        i = info.get("data", {})

        print("=" * 55)
        print("  Synology NAS — System Status")
        print("=" * 55)

        print(f"\n  Model:    {i.get('model', '?')}  (S/N {i.get('serial', '?')})")
        print(f"  DSM:      {i.get('firmware_ver', '?')}")
        print(f"  Uptime:   {i.get('up_time', '?')}")
        print(f"  Temp:     {i.get('sys_temp', '?')}°C{'  ⚠ WARNING' if i.get('sys_tempwarn') else ''}")
        print(f"  Time:     {i.get('time', '?')}  ({i.get('time_zone_desc', '?')})")

        cpu = u.get("cpu", {})
        print(f"\n  CPU:      {cpu.get('1min_load', '?')}% (1m)  "
              f"{cpu.get('5min_load', '?')}% (5m)  "
              f"{cpu.get('15min_load', '?')}% (15m)  "
              f"[user {cpu.get('user_load', '?')}%  sys {cpu.get('system_load', '?')}%]")

        mem = u.get("memory", {})
        total_mb = mem.get("total_real", 0) // 1024
        avail_mb = mem.get("avail_real", 0) // 1024
        used_mb  = total_mb - avail_mb
        print(f"  RAM:      {used_mb} MB used / {total_mb} MB total  ({mem.get('real_usage', '?')}%)")

        net = u.get("network", [])
        ifaces = [n for n in net if n.get("device") != "total"]
        if ifaces:
            print("\n  Network:")
            for iface in ifaces:
                rx = bytes_per_sec(iface.get("rx", 0))
                tx = bytes_per_sec(iface.get("tx", 0))
                print(f"    {iface.get('device', '?'):<8}  rx {rx:<14} tx {tx}")

        disk = u.get("disk", {})
        total = disk.get("total", {})
        print(f"\n  Disk I/O: rd {bytes_per_sec(total.get('read_byte', 0))}  "
              f"wr {bytes_per_sec(total.get('write_byte', 0))}")

        print()

    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
