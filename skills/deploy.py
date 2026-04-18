"""
/synology-deploy <repo-url> <target-path> [--branch <branch>]
  Clone or update a repo on the NAS and run docker compose up -d.

/synology-deploy <target-path> --update
  Pull latest commits + docker compose up -d (no clone).

For private repos, use SSH URLs (preferred — no tokens in plain text):
  git@github.com:user/repo.git
Run /synology-setup-deploy-key once to set up the NAS SSH key for GitHub.

Steps:
  1. mkdir -p parent dir if needed
  2. git clone (first time) or git pull (update)
  3. If .env.example exists but .env doesn't: copy it (leave secrets blank for you to fill)
  4. docker compose up -d
  5. docker compose ps (show final state)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, sudo_run, DOCKER


def https_to_ssh(url):
    """Convert https://github.com/user/repo.git -> git@github.com:user/repo.git"""
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
        return f"git@github.com:{path}"
    return url


def main():
    args = sys.argv[1:]
    update_only = "--update" in args
    args = [a for a in args if a != "--update"]

    branch = "main"
    if "--branch" in args:
        idx = args.index("--branch")
        branch = args[idx + 1]
        args = [a for a in args if a not in ("--branch", branch)]

    if update_only:
        if len(args) < 1:
            print("Usage: deploy.py <target-path> --update")
            sys.exit(1)
        repo_url = None
        target = args[0]
    else:
        if len(args) < 2:
            print("Usage: deploy.py <repo-url> <target-path> [--branch <branch>]")
            print("       deploy.py <target-path> --update")
            print("\nFor private repos, use SSH URL: git@github.com:user/repo.git")
            print("Run /synology-setup-deploy-key first to configure NAS SSH key.")
            sys.exit(1)
        repo_url = args[0]
        target   = args[1]

    # Prefer SSH URLs — auto-convert HTTPS GitHub URLs
    clone_url = repo_url
    if clone_url and clone_url.startswith("https://github.com/"):
        clone_url = https_to_ssh(clone_url)
        print(f"Using SSH URL: {clone_url}")

    client = get_client()
    try:
        # Resolve the deploy key path dynamically if charles's home differs.
        # Per-repo SSH host aliases (e.g. git@github-claude-enphase:...) are
        # set up by `synology add-deploy-key` and use ~/.ssh/config routing —
        # no GIT_SSH_COMMAND override needed for those.
        # Fall back to explicit key for legacy git@github.com: URLs.
        home, _, _ = run(client, "echo $HOME")
        home = home.strip()
        deploy_key = f"{home}/.ssh/github_deploy"
        if clone_url and "git@github.com:" in (clone_url or ""):
            git_ssh = f"GIT_SSH_COMMAND='ssh -i {deploy_key} -o StrictHostKeyChecking=accept-new'"
        else:
            git_ssh = ""  # rely on ~/.ssh/config Host alias routing

        # ── Step 1/2: Clone or pull ────────────────────────────────────────────
        out = sudo_run(client, f"test -d {target}/.git && echo EXISTS || echo MISSING")

        if "MISSING" in out:
            if update_only:
                print(f"No git repo found at {target}. Use clone mode instead.")
                sys.exit(1)
            print(f"Cloning {repo_url}\n  -> {target}  (branch: {branch}) ...")
            parent = "/".join(target.rstrip("/").split("/")[:-1])
            sudo_run(client, f"mkdir -p {parent}")
            branch_flag = f"--branch {branch}" if branch != "main" else ""
            out = sudo_run(client,
                f"{git_ssh} git clone {branch_flag} {clone_url} {target} 2>&1",
                timeout=60)
            print(out or "Cloned OK")
        else:
            print(f"Updating {target} ...")
            out = sudo_run(client,
                f"sh -c 'cd {target} && {git_ssh} git pull 2>&1'", timeout=30)
            print(out or "Already up to date")

        # ── Step 3: Bootstrap .env if missing ─────────────────────────────────
        out = sudo_run(client,
            f"test -f {target}/.env.example && echo HAS_EXAMPLE || echo NO_EXAMPLE")
        if "HAS_EXAMPLE" in out:
            out2 = sudo_run(client,
                f"test -f {target}/.env && echo HAS_ENV || echo NO_ENV")
            if "NO_ENV" in out2:
                sudo_run(client, f"cp {target}/.env.example {target}/.env")
                print(f"\nCreated {target}/.env from .env.example")
                print(f"  >> Edit {target}/.env to fill in any required secrets before proceeding.")
            else:
                print(f"\n.env already exists at {target}/.env")

        # ── Step 4: docker compose up -d ──────────────────────────────────────
        out = sudo_run(client,
            f"test -f {target}/docker-compose.yml -o -f {target}/compose.yml && echo OK || echo MISSING")
        if "MISSING" in out:
            print(f"\nNo docker-compose.yml found in {target}. Skipping compose up.")
            return

        print("\nStarting containers ...")
        out = sudo_run(client,
            f"sh -c 'cd {target} && {DOCKER} compose up -d 2>&1'", timeout=120)
        print(out)

        # ── Step 5: Final state ────────────────────────────────────────────────
        print("\nContainer status:")
        out = sudo_run(client,
            f"sh -c 'cd {target} && {DOCKER} compose ps 2>&1'")
        print(out)

    finally:
        client.close()


if __name__ == "__main__":
    main()
