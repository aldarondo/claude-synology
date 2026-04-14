"""
/synology-ssh "<command>" — Run a shell command on the NAS via SSH.
Uses sudo for commands that require it. Prompts for confirmation on destructive ops.

Usage:
  ssh_shell.py "ls /volume1/docker"
  ssh_shell.py "cat /etc/hostname"
  ssh_shell.py "docker ps" --sudo
  ssh_shell.py "rm -rf /tmp/test" --yes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, sudo_run

DESTRUCTIVE_PATTERNS = ["rm ", "rmdir", "mkfs", "dd ", "shutdown", "reboot",
                        "halt", "poweroff", "> /", "truncate", "wipefs"]


def looks_destructive(cmd):
    return any(p in cmd.lower() for p in DESTRUCTIVE_PATTERNS)


def main():
    if len(sys.argv) < 2:
        print("Usage: ssh_shell.py \"<command>\" [--sudo] [--yes]")
        sys.exit(1)

    use_sudo    = "--sudo" in sys.argv
    skip_confirm = "--yes" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--sudo", "--yes")]
    command = " ".join(args)

    if looks_destructive(command) and not skip_confirm:
        confirm = input(f"Destructive command: {command}\nType YES to confirm: ")
        if confirm.strip() != "YES":
            print("Aborted.")
            return

    client = get_client()
    try:
        if use_sudo:
            out = sudo_run(client, command)
            print(out)
        else:
            out, err, code = run(client, command)
            if out:
                print(out)
            if err:
                print(f"[stderr] {err}", file=sys.stderr)
            if code != 0:
                sys.exit(code)
    finally:
        client.close()


if __name__ == "__main__":
    main()
