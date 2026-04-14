"""
synology edit-env <path> <KEY=VALUE> [KEY2=VALUE2 ...]
  Set one or more keys in a .env file on the NAS.
  Uses SFTP — values never appear in shell history or process list.
  Creates the file if it doesn't exist.

Examples:
  edit_env.py /volume1/docker/brian-mcp TUNNEL_TOKEN=abc123
  edit_env.py /volume1/docker/myapp DB_PASS=secret PORT=8080
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, sftp_read, sftp_write


def parse_env(text):
    """
    Parse .env file text into an ordered list of (key, raw_line) pairs.
    Preserves comments, blank lines, and original ordering.
    Returns list of (key_or_None, original_line).
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines.append((None, line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            lines.append((key, line))
        else:
            lines.append((None, line))
    return lines


def update_env(text, updates):
    """
    Apply a dict of {key: value} updates to .env file text.
    Updates existing keys in-place, appends new keys at end.
    Returns updated file text.
    """
    lines = parse_env(text)
    remaining = dict(updates)

    new_lines = []
    for key, original in lines:
        if key and key in remaining:
            new_lines.append(f"{key}={remaining.pop(key)}")
        else:
            new_lines.append(original)

    # Append any keys that weren't already in the file
    if remaining:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")  # blank separator
        for k, v in remaining.items():
            new_lines.append(f"{k}={v}")

    result = "\n".join(new_lines)
    if result and not result.endswith("\n"):
        result += "\n"
    return result


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: edit_env.py <nas-path> <KEY=VALUE> [KEY2=VALUE2 ...]")
        sys.exit(1)

    path = args[0]
    updates = {}
    for pair in args[1:]:
        if "=" not in pair:
            print(f"Invalid argument (expected KEY=VALUE): {pair}")
            sys.exit(1)
        k, v = pair.split("=", 1)
        updates[k.strip()] = v

    client = get_client()
    try:
        # Read existing file or start empty
        try:
            current = sftp_read(client, path)
        except FileNotFoundError:
            current = ""

        updated = update_env(current, updates)
        sftp_write(client, path, updated)

        masked = {k: "****" for k in updates}
        print(f"Updated {path}:")
        for k, v in masked.items():
            print(f"  {k}={v}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
