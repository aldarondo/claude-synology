"""
Synology SSH client.
Loads SSH config from config.json["ssh"], connects via paramiko.

config.json SSH block:
  {
    "ssh": {
      "host": "192.168.x.x",
      "port": 2222,
      "username": "charles",
      "password": "your-password"
    }
  }

Two run modes:
  run(client, cmd)        — exec_command (no PTY, no sudo)
  sudo_run(client, cmd)   — PTY shell with password injection (required for sudo on Synology)
"""

import json
import os
import time
import re
import paramiko
import logging

logging.getLogger("paramiko").setLevel(logging.WARNING)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")
DOCKER = "/usr/local/bin/docker"


def load_ssh_config():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    ssh = cfg.get("ssh")
    if not ssh:
        raise RuntimeError(
            "No 'ssh' block in config.json.\n"
            'Add: "ssh": {"host":"192.168.x.x","port":2222,"username":"charles","password":"..."}'
        )
    return ssh


def get_client():
    """Return a connected SSHClient."""
    cfg = load_ssh_config()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cfg["host"],
        port=cfg.get("port", 22),
        username=cfg["username"],
        password=cfg.get("password"),
        key_filename=cfg.get("key_file"),
        timeout=10,
    )
    return client


def run(client, command, timeout=30):
    """
    Run a non-sudo command via exec_command.
    Returns (stdout_str, stderr_str, exit_code).
    """
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out  = stdout.read().decode("utf-8", errors="replace").strip()
    err  = stderr.read().decode("utf-8", errors="replace").strip()
    return out, err, code


def run_checked(client, command, timeout=30):
    """Run a non-sudo command and raise RuntimeError on non-zero exit."""
    out, err, code = run(client, command, timeout=timeout)
    if code != 0:
        raise RuntimeError(f"Command failed (exit {code}):\n  $ {command}\n  {err or out}")
    return out


def sudo_run(client, command, timeout=30):
    """
    Run a command via a PTY shell with sudo + password injection.
    Synology's SSH requires a TTY for sudo password prompts.
    Returns the combined output string.
    """
    cfg = load_ssh_config()
    password = cfg.get("password", "")

    shell = client.invoke_shell(width=220, height=50)
    time.sleep(0.4)
    _flush(shell)  # discard login banner

    shell.send(f"sudo {command}\n")
    time.sleep(0.5)
    chunk = _read_until_prompt_or_password(shell, timeout=8)

    # Synology may ask for password even for administrators
    if re.search(r"[Pp]assword:", chunk):
        shell.send(password + "\n")
        time.sleep(0.5)
        chunk = _read_until_prompt_or_password(shell, timeout=timeout)

    shell.close()
    # Strip ANSI escape codes and the trailing shell prompt
    return _clean(chunk)


def _flush(shell, wait=0.3):
    time.sleep(wait)
    if shell.recv_ready():
        shell.recv(65536)


def _read_until_prompt_or_password(shell, timeout=30, chunk_size=4096):
    """Read until we see a shell prompt ($), password prompt, or username prompt."""
    buf = ""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if shell.recv_ready():
            buf += shell.recv(chunk_size).decode("utf-8", errors="replace")
            # Stop on shell prompt at end of line
            if re.search(r"\$\s*$", buf.rstrip()):
                break
            if re.search(r"[Pp]assword[^:]*:", buf):
                break
            if re.search(r"[Uu]sername[^:]*:", buf):
                break
        else:
            time.sleep(0.1)
    return buf


def _clean(text):
    """Strip ANSI codes, carriage returns, non-ASCII control chars, trailing prompt line."""
    text = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)  # ANSI CSI sequences incl. ?25l/h
    text = text.replace("\r", "")
    # Strip non-ASCII characters (e.g. docker compose spinner/braille progress chars)
    text = text.encode("ascii", errors="ignore").decode("ascii")
    # Remove the trailing shell prompt line (user@host:~$ ...)
    lines = text.splitlines()
    clean = [l for l in lines if not re.search(r"@\w+.*\$\s*$", l)]
    return "\n".join(clean).strip()


if __name__ == "__main__":
    client = get_client()
    cfg = load_ssh_config()
    print(f"Connected to {cfg['host']}:{cfg.get('port', 22)} as {cfg['username']}")

    # Test plain command
    out, err, code = run(client, "uname -a")
    print("uname:", out)

    # Test sudo docker ps
    out = sudo_run(client, f"{DOCKER} ps --format '{{{{.Names}}}}\\t{{{{.Status}}}}'")
    print("docker ps:\n", out)

    client.close()
    print("\nSSH OK")
