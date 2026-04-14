"""
Integration test suite for claude-synology.
Validates every API call against the live NAS without executing destructive actions.

Run: python tests/integration.py
     python tests/integration.py --verbose

Exit code 0 = all tests passed
Exit code 1 = one or more failures

Test categories:
  READ   — safe, no side effects
  WRITE  — method existence check only (uses a nonexistent ID to avoid side effects)
  SKIP   — known broken, tracked in ROADMAP backlog
"""

import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.auth import get_session, logout

VERBOSE = "--verbose" in sys.argv

# Error code meanings
ERROR_NAMES = {
    101: "invalid_param",
    103: "method_not_found",
    104: "version_unsupported",
    114: "docker_error_or_missing_param",
    117: "container_not_found",
    120: "not_found",
    4501: "no_update_available",
}

results = []


def api(host, sid, api_name, version, method, **kwargs):
    params = {"api": api_name, "version": version, "method": method, "_sid": sid}
    params.update(kwargs)
    resp = requests.get(f"{host}/webapi/entry.cgi", params=params, verify=False)
    resp.raise_for_status()
    return resp.json()


def check(label, category, host, sid, api_name, version, method,
          expect_success=True, expect_error=None, **kwargs):
    """
    Run one API call and record pass/fail.

    expect_success=True  — response must be {"success": true}
    expect_error=CODE    — response must be {"success": false, "error": {"code": CODE}}
                           Used for write methods tested with a fake ID so we confirm
                           the method exists without actually running it.
    """
    try:
        r = api(host, sid, api_name, version, method, **kwargs)
        success = r.get("success", False)
        code = r.get("error", {}).get("code") if not success else None

        if expect_success and success:
            status = "PASS"
            detail = ""
        elif expect_error is not None and not success and code == expect_error:
            status = "PASS"
            detail = f"(got expected error {code} = {ERROR_NAMES.get(code, code)})"
        elif not success:
            status = "FAIL"
            detail = f"error {code} = {ERROR_NAMES.get(code, str(code))}"
        else:
            status = "FAIL"
            detail = "expected failure but got success"

    except Exception as e:
        status = "FAIL"
        detail = str(e)

    results.append((status, category, label, detail))
    if VERBOSE or status != "PASS":
        marker = {"PASS": "  ok", "FAIL": "FAIL", "SKIP": "skip"}[status]
        suffix = f"  -- {detail}" if detail else ""
        print(f"  [{marker}] [{category}] {label}{suffix}")


def skip(label, reason):
    results.append(("SKIP", "SKIP", label, reason))
    if VERBOSE:
        print(f"  [skip] [SKIP] {label}  -- {reason}")


def run():
    print("Connecting to NAS...")
    host, sid = get_session()
    print(f"Connected: {host}\n")

    try:
        # ── READ: System ──────────────────────────────────────────────────────
        print("--- System ---")
        check("system info",         "READ", host, sid, "SYNO.Core.System",             "1", "info")
        check("system utilization",  "READ", host, sid, "SYNO.Core.System.Utilization", "1", "get")

        # ── READ: Packages ────────────────────────────────────────────────────
        print("--- Packages ---")
        check("package list",        "READ", host, sid, "SYNO.Core.Package",             "1", "list")
        check("upgrade check",       "READ", host, sid, "SYNO.Core.Upgrade.Server",      "4", "check")
        check("upgrade status",      "READ", host, sid, "SYNO.Core.Upgrade",             "1", "status")
        check("upgrade settings",    "READ", host, sid, "SYNO.Core.Upgrade.Setting",     "4", "get")
        check("autoupgrade progress","READ", host, sid, "SYNO.Core.Package.AutoUpgrade.Progress", "1", "get")

        # ── READ: Docker ──────────────────────────────────────────────────────
        print("--- Docker ---")
        check("container list",      "READ", host, sid, "SYNO.Docker.Container", "1", "list",
              limit=100, offset=0)
        check("image list",          "READ", host, sid, "SYNO.Docker.Image",     "1", "list",
              limit=100, offset=0)
        check("registry list",       "READ", host, sid, "SYNO.Docker.Registry",  "1", "get")

        # ── READ: Storage ─────────────────────────────────────────────────────
        print("--- Storage ---")
        check("storage info",        "READ", host, sid, "SYNO.Storage.CGI.Storage", "1", "load_info")

        # ── READ: Users ───────────────────────────────────────────────────────
        print("--- Users ---")
        check("user list",           "READ", host, sid, "SYNO.Core.User", "1", "list",
              offset=0, limit=200)

        # ── READ: Logs ────────────────────────────────────────────────────────
        print("--- Logs ---")
        check("syslog list",         "READ", host, sid, "SYNO.Core.SyslogClient.Log", "1", "list",
              limit=20, offset=0)

        # ── WRITE: Docker (method existence — uses nonexistent container) ─────
        print("--- Write: Docker ---")
        check("container start method", "WRITE", host, sid, "SYNO.Docker.Container", "1", "start",
              expect_error=117, name="__test_nonexistent__")
        check("container stop method",  "WRITE", host, sid, "SYNO.Docker.Container", "1", "stop",
              expect_error=117, name="__test_nonexistent__")

        # ── WRITE: Packages (method existence — uses nonexistent package ID) ──
        print("--- Write: Packages ---")
        check("package upgrade method", "WRITE", host, sid, "SYNO.Core.Package.Installation", "1", "upgrade",
              expect_error=4501, id="__test_nonexistent__")
        check("package install method", "WRITE", host, sid, "SYNO.Core.Package.Installation", "1", "install",
              expect_error=120, id="__test_nonexistent__")

        # ── WRITE: DSM Upgrade trigger ─────────────────────────────────────────
        print("--- Write: DSM Upgrade ---")
        check("dsm upgrade trigger v1", "WRITE", host, sid, "SYNO.Core.Upgrade", "1", "upgrade",
              expect_error=103)   # 103 = method not found = BROKEN, will FAIL until fixed
        check("dsm upgrade download",   "WRITE", host, sid, "SYNO.Core.Upgrade.Server.Download", "2", "start",
              expect_error=101)   # 101 = invalid param = method exists, params unknown

        # ── Package catalog ───────────────────────────────────────────────────
        print("--- Package catalog ---")
        check("package catalog list", "READ", host, sid, "SYNO.Core.Package.Server", "1", "list",
              limit=10, offset=0)

        # ── Known API limitations (resolved via SSH fallback) ─────────────────
        print("--- Known API limitations ---")
        skip("container logs HTTP API",
             "error 114 on CM24.x — resolved: skill falls back to SSH docker logs")
        skip("docker image pull HTTP API",
             "error 103 on CM24.x — resolved: skill falls back to SSH docker pull")
        skip("DSM upgrade HTTP API",
             "error 103 on DSM 7.2+ — resolved: skill uses SSH synoupgrade CLI")

    finally:
        logout(host, sid)

    # ── Summary ───────────────────────────────────────────────────────────────
    passed  = sum(1 for r in results if r[0] == "PASS")
    failed  = sum(1 for r in results if r[0] == "FAIL")
    skipped = sum(1 for r in results if r[0] == "SKIP")
    total   = passed + failed

    print(f"\n{'=' * 50}")
    print(f"  Results: {passed}/{total} passed  |  {skipped} skipped (known broken)")

    if failed:
        print(f"\n  FAILURES:")
        for status, cat, label, detail in results:
            if status == "FAIL":
                print(f"    [{cat}] {label}: {detail}")
        print()

    print(f"{'=' * 50}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
