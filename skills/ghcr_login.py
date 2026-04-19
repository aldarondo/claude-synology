"""
/synology ghcr-login [--username U] [--token T]
  Authenticate Docker on the NAS to ghcr.io.
  Token is piped via stdin — never appears in shell history or process list.

  Credentials can also live in config.json:
    "ghcr": { "username": "your-github-user", "token": "ghp_..." }

  PAT requires read:packages scope (add write:packages if you push from the NAS).
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, DOCKER

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def main():
    args = sys.argv[1:]
    username = None
    token = None

    i = 0
    while i < len(args):
        if args[i] == "--username" and i + 1 < len(args):
            username = args[i + 1]
            i += 2
        elif args[i] == "--token" and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        else:
            i += 1

    # Fall back to config.json
    if not username or not token:
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            ghcr = cfg.get("ghcr", {})
            username = username or ghcr.get("username")
            token = token or ghcr.get("token")
        except Exception:
            pass

    if not username or not token:
        print("Usage: synology ghcr-login --username <github-user> --token <PAT>")
        print("       Or add to config.json: \"ghcr\": {\"username\": \"...\", \"token\": \"...\"}")
        print("\nPAT requires read:packages scope.")
        sys.exit(1)

    client = get_client()
    try:
        print(f"Logging in to ghcr.io as {username} ...")
        # exec_command pipes token via stdin — never on the command line
        stdin, stdout, stderr = client.exec_command(
            f"{DOCKER} login ghcr.io -u {username} --password-stdin"
        )
        stdin.write(token.encode("utf-8"))
        stdin.channel.shutdown_write()
        code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        if code == 0:
            print(out or "Login succeeded.")
        else:
            print(f"Login failed (exit {code}):")
            print(err or out)
            sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
