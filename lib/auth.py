"""
Synology DSM session auth.
Loads config from config.json, logs in via SYNO.API.Auth, returns a SID token.
All skills import get_session() / logout().
"""

import json
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_session():
    """Log in and return (host, sid)."""
    cfg = load_config()
    host = cfg["host"].rstrip("/")
    params = {
        "api": "SYNO.API.Auth",
        "version": "3",
        "method": "login",
        "account": cfg["username"],
        "passwd": cfg["password"],
        "session": "ClaudeSession",
        "format": "sid",
    }
    resp = requests.get(
        f"{host}/webapi/auth.cgi",
        params=params,
        verify=cfg.get("verify_ssl", False),
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Auth failed: {data.get('error')}")
    sid = data["data"]["sid"]
    return host, sid


def logout(host, sid):
    """Invalidate the session."""
    requests.get(
        f"{host}/webapi/auth.cgi",
        params={
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "logout",
            "session": "ClaudeSession",
            "_sid": sid,
        },
        verify=False,
    )


if __name__ == "__main__":
    host, sid = get_session()
    print(f"Connected to {host}")
    print(f"SID: {sid[:8]}...")
    logout(host, sid)
    print("Logged out OK")
