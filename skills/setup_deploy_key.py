"""
/synology-setup-deploy-key — Generate an SSH deploy key on the NAS for GitHub access.

Run once per NAS. After running:
  1. Copy the public key printed here
  2. Go to GitHub repo > Settings > Deploy keys > Add deploy key
  3. Paste the key, name it "Synology NAS", leave "Allow write access" unchecked
  4. Use SSH-format URLs with /synology-deploy: git@github.com:user/repo.git

The key is stored at ~/.ssh/github_deploy on the NAS (in the SSH user's home directory).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.ssh import get_client, run, run_checked

KEY_PATH = "~/.ssh/github_deploy"


def main():
    client = get_client()
    try:
        # Resolve ~ to the actual home directory
        home, _, _ = run(client, "echo $HOME")
        home = home.strip()
        ssh_dir = f"{home}/.ssh"
        key_file = f"{ssh_dir}/github_deploy"

        # Ensure .ssh directory exists with correct permissions
        run_checked(client, f"mkdir -p {ssh_dir} && chmod 700 {ssh_dir}")

        # Check if key already exists
        _, _, code = run(client, f"test -f {key_file}")
        if code == 0:
            print(f"Deploy key already exists at {key_file} on the NAS.\n")
        else:
            print("Generating SSH deploy key on NAS ...")
            out, err, code = run(client,
                f'ssh-keygen -t ed25519 -C "synology-nas-deploy" -f {key_file} -N ""')
            if code != 0:
                print(f"Error generating key: {err or out}")
                sys.exit(1)
            run(client, f"chmod 600 {key_file}")
            print("Key generated.\n")

        # Add GitHub to known_hosts (suppress duplicates)
        _, _, code = run(client, "grep -q 'github.com' ~/.ssh/known_hosts 2>/dev/null")
        if code != 0:
            print("Adding github.com to known_hosts ...")
            out, err, code = run(client,
                "ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null",
                timeout=15)
            if code == 0:
                print("Done.\n")
            else:
                print(f"Warning: ssh-keyscan failed: {err}\n")
        else:
            print("github.com already in known_hosts.\n")

        # Configure SSH to use the deploy key for github.com
        ssh_config = f"{ssh_dir}/config"
        _, _, code = run(client, f"grep -q 'github_deploy' {ssh_config} 2>/dev/null")
        if code != 0:
            config_block = (
                f"Host github.com\n"
                f"  HostName github.com\n"
                f"  User git\n"
                f"  IdentityFile {key_file}\n"
                f"  IdentitiesOnly yes\n"
            )
            # Write via python to avoid shell quoting issues
            run_checked(client,
                f"python3 -c \""
                f"open('{ssh_config}', 'a').write("
                f"'\\nHost github.com\\n"
                f"  HostName github.com\\n"
                f"  User git\\n"
                f"  IdentityFile {key_file}\\n"
                f"  IdentitiesOnly yes\\n')"
                f"\"")
            run(client, f"chmod 600 {ssh_config}")
            print("SSH config updated to use deploy key for github.com.\n")
        else:
            print("SSH config already references deploy key.\n")

        # Print the public key
        pub_key, _, _ = run(client, f"cat {key_file}.pub")
        print("=" * 60)
        print("PUBLIC KEY -- add this to GitHub:")
        print("=" * 60)
        print(pub_key)
        print("=" * 60)
        print("\nSteps:")
        print("  1. Copy the key above")
        print("  2. GitHub repo > Settings > Deploy keys > Add deploy key")
        print("  3. Name: 'Synology NAS'  |  Allow write access: NO")
        print("  4. Deploy with: /synology-deploy git@github.com:user/repo.git /volume1/docker/repo")

    finally:
        client.close()


if __name__ == "__main__":
    main()
