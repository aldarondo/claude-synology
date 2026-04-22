"""
synology file <subcommand> — File operations on the NAS via SFTP/SSH.

Subcommands:
  read <path>              Print file contents
  list <path>              List directory contents
  exists <path>            Check if a file or directory exists
  delete <path>            Delete a file (requires YES confirmation)

Examples:
  file_ops.py read  /volume1/docker/brian-mcp/.env
  file_ops.py list  /volume1/docker
  file_ops.py exists /volume1/docker/brian-mcp/.env
  file_ops.py delete /volume1/docker/brian-mcp/old-file.log
"""

import shlex
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, sudo_run, sftp_read

USAGE = """\
Usage: file_ops.py <subcommand> [args...]

Subcommands:
  read   <path>    Print file contents
  list   <path>    List directory (ls -lh)
  exists <path>    Check if file/directory exists (exit 0=yes, 1=no)
  delete <path>    Delete a file (prompts YES; use --yes to skip)
"""


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(1)

    sub  = args[0].lower()
    rest = args[1:]

    if sub == "read":
        if not rest:
            print("Usage: file_ops.py read <path>")
            sys.exit(1)
        path = rest[0]
        client = get_client()
        try:
            try:
                content = sftp_read(client, path)
                print(content, end="")
            except (FileNotFoundError, IOError):
                # Fall back to sudo cat for root-owned files
                out = sudo_run(client, f"cat {shlex.quote(path)} 2>&1")
                if "No such file" in out or "Permission denied" in out:
                    print(f"Error: {out}", file=sys.stderr)
                    sys.exit(1)
                print(out)
        finally:
            client.close()

    elif sub == "list":
        path = rest[0] if rest else "."
        client = get_client()
        try:
            out = sudo_run(client, f"ls -lh {shlex.quote(path)} 2>&1")
            print(out)
        finally:
            client.close()

    elif sub == "exists":
        if not rest:
            print("Usage: file_ops.py exists <path>")
            sys.exit(1)
        path = rest[0]
        client = get_client()
        try:
            _, _, code = run(client, f"test -e {shlex.quote(path)}")
            if code == 0:
                print(f"EXISTS: {path}")
                sys.exit(0)
            else:
                print(f"MISSING: {path}")
                sys.exit(1)
        finally:
            client.close()

    elif sub == "delete":
        if not rest:
            print("Usage: file_ops.py delete <path>")
            sys.exit(1)
        path = rest[0]
        skip_confirm = "--yes" in args

        if not skip_confirm:
            confirm = input(f"Delete {path} on NAS? Type YES to confirm: ")
            if confirm.strip() != "YES":
                print("Aborted.")
                return

        client = get_client()
        try:
            out = sudo_run(client, f"rm {shlex.quote(path)} 2>&1")
            if out:
                print(out)
            else:
                print(f"Deleted: {path}")
        finally:
            client.close()

    else:
        print(f"Unknown subcommand: {sub}\n")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
