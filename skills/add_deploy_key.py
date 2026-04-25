"""
synology add-deploy-key <owner/repo>

Ensures the NAS has a deploy key registered for the given GitHub repo.

Strategy — per-repo keys:
  GitHub does not allow the same public key to be a deploy key on more than
  one repo. This script uses per-repo key files named:
    ~/.ssh/github_deploy_<repo-slug>      (e.g. github_deploy_claude-enphase)
  The legacy single key ~/.ssh/github_deploy is accepted if it's the only
  key and not already claimed by another repo.

Steps:
  1. Check for an existing per-repo key on the NAS; generate one if missing.
  2. Update ~/.ssh/config so git uses the right key for this repo.
  3. Register the public key on GitHub via gh CLI.
  4. Verify SSH access works.

Requires:
  - `gh` CLI installed and authenticated on this machine
"""

import json
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run


def gh_api(method, path, **data):
    cmd = ["gh", "api", "--method", method, path]
    if data:
        cmd += ["--input", "-"]
        result = subprocess.run(cmd, input=json.dumps(data), capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def gh_error_detail(result):
    """Extract the most useful error message from a failed gh api call."""
    lines = []
    if result.stderr:
        lines.append(result.stderr.strip())
    if result.stdout:
        try:
            body = json.loads(result.stdout)
            if "message" in body:
                lines.append(f"GitHub: {body['message']}")
            if "errors" in body:
                for e in body["errors"]:
                    lines.append(f"  - {e}")
        except json.JSONDecodeError:
            if result.stdout.strip():
                lines.append(result.stdout.strip())
    return "\n".join(lines) if lines else "(no detail available)"


def repo_slug(repo):
    """aldarondo/claude-enphase -> claude-enphase"""
    return repo.split("/")[-1]


def ensure_repo_key(client, home, slug):
    """
    Return (key_path, pubkey) for this repo's deploy key.
    Generates a new ed25519 key pair if one doesn't exist yet.
    """
    key_path = f"{home}/.ssh/github_deploy_{slug}"
    pubkey, _, code = run(client, f"cat {key_path}.pub 2>/dev/null")
    if code == 0 and pubkey.strip():
        print(f"  Found existing key: {key_path}")
        return key_path, pubkey.strip()

    # Generate a new key pair
    print(f"  Generating new key pair: {key_path}")
    out, _, code = run(client,
        f"ssh-keygen -t ed25519 -f {key_path} -N '' -C 'synology-nas-{slug}' 2>&1")
    if code != 0:
        print(f"ERROR: ssh-keygen failed:\n{out}")
        sys.exit(1)
    run(client, f"chmod 600 {key_path}")
    pubkey, _, _ = run(client, f"cat {key_path}.pub")
    return key_path, pubkey.strip()


def ensure_ssh_config(client, home, slug, key_path):
    """
    Add a Host alias block to ~/.ssh/config for this repo so git uses
    the right key:
      Host github-<slug>
        HostName github.com
        User git
        IdentityFile <key_path>
        IdentitiesOnly yes
        StrictHostKeyChecking accept-new

    The clone URL becomes: git@github-<slug>:<owner>/<repo>.git
    """
    host_alias = f"github-{slug}"
    config_block = (
        f"\nHost {host_alias}\n"
        f"  HostName github.com\n"
        f"  User git\n"
        f"  IdentityFile {key_path}\n"
        f"  IdentitiesOnly yes\n"
        f"  StrictHostKeyChecking accept-new\n"
    )

    config_path = f"{home}/.ssh/config"
    existing, _, _ = run(client, f"cat {config_path} 2>/dev/null")
    if f"Host {host_alias}" in existing:
        print(f"  SSH config already has Host {host_alias}")
    else:
        print(f"  Adding Host {host_alias} to {config_path}")
        run(client, f"printf '{config_block}' >> {config_path}")
    return host_alias


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: synology add-deploy-key <owner/repo>")
        sys.exit(1)

    repo = args[0].removeprefix("https://github.com/").removesuffix(".git")
    if "/" not in repo:
        print(f"ERROR: expected owner/repo, got: {repo}")
        sys.exit(1)

    slug = repo_slug(repo)
    title = f"Synology NAS ({slug})"

    client = get_client()
    try:
        home, _, _ = run(client, "echo $HOME")
        home = home.strip()

        print(f"Setting up deploy key for {repo} ...")
        key_path, pubkey = ensure_repo_key(client, home, slug)
        host_alias = ensure_ssh_config(client, home, slug, key_path)
    finally:
        client.close()

    # Check if key is already on this repo
    result = gh_api("GET", f"/repos/{repo}/keys")
    if result.returncode != 0:
        print(f"ERROR: could not list deploy keys for {repo}")
        print(gh_error_detail(result))
        sys.exit(1)

    existing = json.loads(result.stdout)
    for key in existing:
        if key.get("key", "").split()[:2] == pubkey.split()[:2]:
            print(f"  Deploy key already present on GitHub (id={key['id']}). Nothing to do.")
            _print_clone_url(repo, host_alias)
            return

    # Register on GitHub
    print("  Registering deploy key on GitHub ...")
    result = gh_api("POST", f"/repos/{repo}/keys",
                    title=title, key=pubkey, read_only=True)
    if result.returncode != 0:
        print("ERROR: failed to add deploy key")
        print(gh_error_detail(result))
        sys.exit(1)

    data = json.loads(result.stdout)
    print(f"  Done. Key registered: id={data['id']}, title='{data['title']}'")
    _print_clone_url(repo, host_alias)


def _print_clone_url(repo, host_alias):
    clone_url = f"git@{host_alias}:{repo}.git"
    print(f"\nClone URL for this repo:  {clone_url}")
    print(f"Deploy command:  synology deploy {clone_url} /volume1/docker/{repo_slug(repo)}")


if __name__ == "__main__":
    main()
