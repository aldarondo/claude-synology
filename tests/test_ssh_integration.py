"""
SSH integration tests for claude-synology.
Tests the SSH layer and SSH-based skills against the live NAS.

Requires: SSH configured in config.json["ssh"]
Run: python tests/test_ssh_integration.py
     python tests/test_ssh_integration.py --verbose

Exit code 0 = all tests passed
Exit code 1 = one or more failures

Test categories:
  SSH    — lib/ssh.py primitives (run, sudo_run, sftp)
  SKILL  — skill-level behaviour (edit_env, docker_compose, deploy, etc.)
  SKIP   — known limitations
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, run_checked, sudo_run, sftp_read, sftp_write
from skills.edit_env import parse_env, update_env

VERBOSE = "--verbose" in sys.argv

results = []


# ── Helpers ───────────────────────────────────────────────────────────────────

def record(status, category, label, detail=""):
    results.append((status, category, label, detail))
    if VERBOSE or status != "PASS":
        marker = {"PASS": "  ok", "FAIL": "FAIL", "SKIP": "skip"}[status]
        suffix = f"  -- {detail}" if detail else ""
        print(f"  [{marker}] [{category}] {label}{suffix}")


def check(label, category, fn):
    """Run fn(); record PASS if it returns without raising, FAIL otherwise."""
    try:
        fn()
        record("PASS", category, label)
    except AssertionError as e:
        record("FAIL", category, label, str(e))
    except Exception as e:
        record("FAIL", category, label, f"{type(e).__name__}: {e}")


def skip(label, reason):
    record("SKIP", "SKIP", label, reason)


# ── SSH primitives ────────────────────────────────────────────────────────────

def test_ssh_primitives(client):
    print("--- SSH primitives ---")

    def t_connect():
        out, err, code = run(client, "echo hello")
        assert code == 0, f"exit code {code}"
        assert "hello" in out, f"unexpected output: {out!r}"
    check("connect and run", "SSH", t_connect)

    def t_run_exit_code():
        _, _, code = run(client, "true")
        assert code == 0
        _, _, code = run(client, "false")
        assert code != 0
    check("run exit codes", "SSH", t_run_exit_code)

    def t_run_checked_raises():
        raised = False
        try:
            run_checked(client, "false")
        except RuntimeError:
            raised = True
        assert raised, "run_checked should raise on non-zero exit"
    check("run_checked raises on failure", "SSH", t_run_checked_raises)

    def t_sudo_run():
        out = sudo_run(client, "whoami")
        assert out.strip() != "", "sudo_run returned empty output"
    check("sudo_run executes", "SSH", t_sudo_run)

    def t_uname():
        out, _, code = run(client, "uname -s")
        assert code == 0
        assert "Linux" in out, f"expected Linux, got: {out!r}"
    check("NAS is Linux", "SSH", t_uname)

    def t_home_dir():
        out, _, code = run(client, "echo $HOME")
        assert code == 0
        assert out.strip() != "", "HOME is empty"
        assert out.strip().startswith("/"), f"HOME not absolute: {out!r}"
    check("home directory accessible", "SSH", t_home_dir)


# ── SFTP ──────────────────────────────────────────────────────────────────────

def test_sftp(client):
    print("--- SFTP ---")

    home, _, _ = run(client, "echo $HOME")
    home = home.strip()
    test_file = f"{home}/.claude_synology_test"

    def t_write_read():
        sftp_write(client, test_file, "hello=world\n")
        content = sftp_read(client, test_file)
        assert "hello=world" in content, f"unexpected content: {content!r}"
    check("sftp write then read", "SSH", t_write_read)

    def t_roundtrip_unicode_safe():
        sftp_write(client, test_file, "KEY=value with spaces\nOTHER=123\n")
        content = sftp_read(client, test_file)
        assert "KEY=value with spaces" in content
        assert "OTHER=123" in content
    check("sftp roundtrip preserves content", "SSH", t_roundtrip_unicode_safe)

    def t_overwrite():
        sftp_write(client, test_file, "FIRST=1\n")
        sftp_write(client, test_file, "SECOND=2\n")
        content = sftp_read(client, test_file)
        assert "SECOND=2" in content
        assert "FIRST" not in content
    check("sftp overwrite replaces file", "SSH", t_overwrite)

    def t_read_missing():
        raised = False
        try:
            sftp_read(client, f"{home}/.nonexistent_file_12345")
        except (FileNotFoundError, IOError):
            raised = True
        assert raised, "sftp_read should raise on missing file"
    check("sftp_read raises on missing file", "SSH", t_read_missing)

    # Cleanup
    run(client, f"rm -f {test_file}")


# ── edit_env skill ────────────────────────────────────────────────────────────

def test_edit_env(client):
    print("--- edit_env skill ---")

    home, _, _ = run(client, "echo $HOME")
    home = home.strip()
    env_file = f"{home}/.claude_synology_test.env"

    def t_create_new():
        # Start from scratch
        run(client, f"rm -f {env_file}")
        from skills.edit_env import update_env
        sftp_write(client, env_file, update_env("", {"TOKEN": "abc", "PORT": "8080"}))
        content = sftp_read(client, env_file)
        assert "TOKEN=abc" in content
        assert "PORT=8080" in content
    check("create new .env with keys", "SKILL", t_create_new)

    def t_update_existing():
        sftp_write(client, env_file, "TOKEN=old\nPORT=8080\n")
        from skills.edit_env import update_env
        current = sftp_read(client, env_file)
        sftp_write(client, env_file, update_env(current, {"TOKEN": "new"}))
        content = sftp_read(client, env_file)
        assert "TOKEN=new" in content
        assert "TOKEN=old" not in content
        assert "PORT=8080" in content, "existing key should be preserved"
    check("update existing key preserves others", "SKILL", t_update_existing)

    def t_append_key():
        sftp_write(client, env_file, "EXISTING=yes\n")
        from skills.edit_env import update_env
        current = sftp_read(client, env_file)
        sftp_write(client, env_file, update_env(current, {"NEW_KEY": "hello"}))
        content = sftp_read(client, env_file)
        assert "EXISTING=yes" in content
        assert "NEW_KEY=hello" in content
    check("append new key to existing file", "SKILL", t_append_key)

    # Cleanup
    run(client, f"rm -f {env_file}")


# ── SSH shell ─────────────────────────────────────────────────────────────────

def test_ssh_shell(client):
    print("--- ssh_shell ---")

    def t_safe_command():
        out = sudo_run(client, "df -h /volume1")
        assert "/volume1" in out, f"expected /volume1 in output: {out!r}"
    check("df /volume1 returns output", "SKILL", t_safe_command)

    def t_docker_ps():
        from lib.ssh import DOCKER
        out = sudo_run(client, f"{DOCKER} ps --format '{{{{.Names}}}}'")
        assert out.strip() != "", "expected at least one running container"
    check("docker ps returns containers", "SKILL", t_docker_ps)

    def t_nonexistent_command():
        _, _, code = run(client, "command_that_does_not_exist_xyz 2>/dev/null")
        assert code != 0, "nonexistent command should return non-zero"
    check("nonexistent command returns non-zero", "SKILL", t_nonexistent_command)


# ── deploy key ────────────────────────────────────────────────────────────────

def test_deploy_key(client):
    print("--- deploy key ---")

    home, _, _ = run(client, "echo $HOME")
    home = home.strip()

    def t_key_exists():
        _, _, code = run(client, f"test -f {home}/.ssh/github_deploy")
        assert code == 0, f"Deploy key not found at {home}/.ssh/github_deploy"
    check("github_deploy key exists on NAS", "SKILL", t_key_exists)

    def t_pub_key_exists():
        _, _, code = run(client, f"test -f {home}/.ssh/github_deploy.pub")
        assert code == 0, "Deploy public key not found"
    check("github_deploy.pub exists on NAS", "SKILL", t_pub_key_exists)

    def t_ssh_config_references_key():
        out, _, _ = run(client, f"cat {home}/.ssh/config 2>/dev/null")
        assert "github_deploy" in out, "SSH config does not reference deploy key"
        assert "github.com" in out, "SSH config does not have github.com Host entry"
    check("SSH config references deploy key", "SKILL", t_ssh_config_references_key)


# ── docker compose ────────────────────────────────────────────────────────────

def test_docker_compose(client):
    print("--- docker compose (SSH) ---")

    from lib.ssh import DOCKER

    def t_brian_mcp_exists():
        _, _, code = run(client, "test -d /volume1/docker/brian-mcp/.git")
        assert code == 0, "brian-mcp repo not found at /volume1/docker/brian-mcp"
    check("brian-mcp repo cloned on NAS", "SKILL", t_brian_mcp_exists)

    def t_compose_file_exists():
        _, _, code = run(client, "test -f /volume1/docker/brian-mcp/docker-compose.yml")
        assert code == 0, "docker-compose.yml not found in brian-mcp"
    check("brian-mcp compose file present", "SKILL", t_compose_file_exists)

    def t_compose_ps():
        out = sudo_run(client,
            "sh -c 'cd /volume1/docker/brian-mcp && "
            f"{DOCKER} compose ps 2>&1'")
        assert "brian-mcp" in out, f"expected brian-mcp containers in ps output: {out!r}"
    check("docker compose ps returns brian-mcp containers", "SKILL", t_compose_ps)

    def t_env_file_exists():
        _, _, code = run(client, "test -f /volume1/docker/brian-mcp/.env")
        assert code == 0, ".env file missing from brian-mcp"
    check("brian-mcp .env file present", "SKILL", t_env_file_exists)

    skip("docker compose logs live tail",
         "120s PTY timeout truncates long-running log streams")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_all():
    print("Connecting to NAS via SSH...")
    client = get_client()
    print("Connected.\n")

    try:
        test_ssh_primitives(client)
        test_sftp(client)
        test_edit_env(client)
        test_ssh_shell(client)
        test_deploy_key(client)
        test_docker_compose(client)
    finally:
        client.close()

    passed  = sum(1 for r in results if r[0] == "PASS")
    failed  = sum(1 for r in results if r[0] == "FAIL")
    skipped = sum(1 for r in results if r[0] == "SKIP")
    total   = passed + failed

    print(f"\n{'=' * 50}")
    print(f"  Results: {passed}/{total} passed  |  {skipped} skipped")

    if failed:
        print(f"\n  FAILURES:")
        for status, cat, label, detail in results:
            if status == "FAIL":
                print(f"    [{cat}] {label}: {detail}")

    print(f"{'=' * 50}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_all())
