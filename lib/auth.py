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
import logging
import os
import requests
import urllib3

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"host", "username", "password"}


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(
            f"config.json not found at {CONFIG_PATH}.\n"
            "Copy config.example.json to config.json and fill in your NAS details."
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"config.json is not valid JSON: {exc}")

    missing = REQUIRED_KEYS - cfg.keys()
    if missing:
        raise RuntimeError(
            f"config.json is missing required keys: {', '.join(sorted(missing))}\n"
            "Required: host, username, password"
        )
    return cfg


def _get_verify():
    """Return verify_ssl from config, defaulting to False on any read error."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f).get("verify_ssl", False)
    except Exception:
        return False


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

    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    verify = _get_verify()
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
            verify=verify,
            timeout=5,
        )
    except Exception as exc:
        logger.warning("Session logout failed (best-effort): %s", exc)


def api_get(host, sid, api, version, method, **extra):
    """Convenience wrapper for DSM API GET calls."""
    verify = _get_verify()
    params = {"api": api, "version": version, "method": method, "_sid": sid}
    params.update(extra)
    resp = requests.get(f"{host}/webapi/entry.cgi", params=params, verify=verify)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    host, sid = get_session()
    print(f"Connected to {host}")
    print(f"SID: {sid[:8]}...")
    logout(host, sid)
    print("Logged out OK")
