"""
Synology DSM session auth.
Loads config from config.json, logs in via SYNO.API.Auth, returns a SID token.
All skills import get_session() / logout().

Port conventions:
  5000 = HTTP only  (use http://host:5000)
  5001 = HTTPS only (use https://host:5001)
If the config uses https:// on port 5000, we auto-correct to http://.
Credentials are sent via POST body, not URL params.
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


def _fix_host(host):
    """
    Correct common config mistakes:
    - https://x:5000 → http://x:5000  (port 5000 is HTTP-only on DSM)
    - http://x:5001  → https://x:5001 (port 5001 is HTTPS-only on DSM)
    """
    if host.startswith("https://") and ":5000" in host:
        host = "http://" + host[len("https://"):]
    elif host.startswith("http://") and ":5001" in host:
        host = "https://" + host[len("http://"):]
    return host


def get_session():
    """Log in and return (host, sid). Credentials sent via POST, not URL."""
    cfg = load_config()
    host = _fix_host(cfg["host"].rstrip("/"))
    verify = cfg.get("verify_ssl", False)

    data = {
        "api": "SYNO.API.Auth",
        "version": "3",
        "method": "login",
        "account": cfg["username"],
        "passwd": cfg["password"],
        "session": "ClaudeSession",
        "format": "sid",
    }
    resp = requests.post(
        f"{host}/webapi/auth.cgi",
        data=data,
        verify=verify,
    )
    resp.raise_for_status()
    result = resp.json()
    if not result.get("success"):
        error = result.get("error", {})
        raise RuntimeError(f"Auth failed (code {error.get('code', '?')}): {error}")
    sid = result["data"]["sid"]
    return host, sid


def logout(host, sid):
    """Invalidate the session."""
    try:
        requests.post(
            f"{host}/webapi/auth.cgi",
            data={
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "logout",
                "session": "ClaudeSession",
                "_sid": sid,
            },
            verify=False,
            timeout=5,
        )
    except Exception:
        pass  # best-effort logout


def api_get(host, sid, api, version, method, **extra):
    """Convenience wrapper for DSM API GET calls."""
    params = {"api": api, "version": version, "method": method, "_sid": sid}
    params.update(extra)
    resp = requests.get(f"{host}/webapi/entry.cgi", params=params, verify=False)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    host, sid = get_session()
    print(f"Connected to {host}")
    print(f"SID: {sid[:8]}...")
    logout(host, sid)
    print("Logged out OK")
