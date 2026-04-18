# claude-synology

Manage a Synology NAS from Claude Code via a single `/synology` slash command. All operations go through one dispatcher — type `/synology` with no arguments to see the full command reference.

## Quick Start

1. Copy `config.example.json` → `config.json` and fill in your NAS details
2. `config.json` is gitignored — never commit it
3. Install dependencies: `pip install -r requirements.txt`
4. Test HTTP API connection: `python lib/auth.py`
5. Test SSH connection: `python lib/ssh.py`

## Configuration

```json
{
  "host": "http://192.168.x.x:5000",
  "username": "admin",
  "password": "your-password",
  "verify_ssl": false,
  "ssh": {
    "host": "192.168.x.x",
    "port": 2222,
    "username": "your-nas-user",
    "password": "your-password"
  }
}
```

Port notes: `5000` = HTTP, `5001` = HTTPS. `lib/auth.py` auto-corrects if you mix them up.  
SSH requires DSM > Control Panel > Terminal & SNMP > Enable SSH service.

## Command Reference

All commands run via: `python skills/synology.py <command> [args]`

### System
| Command | Description |
|---|---|
| `status` | Dashboard — DSM version, CPU, RAM, temp, network, disk I/O |
| `health` | Aggregated health check — storage %, RAID, disk temps/SMART, containers, DSM update |
| `storage` | Volume usage bars, RAID pool table, disk temps and S.M.A.R.T |
| `network` | Network interfaces, IPs, gateway, DNS |
| `logs [--level L] [--lines N] [--type T]` | System log viewer with filters |
| `users` | NAS users with email and group memberships |
| `backup` | Hyper Backup task status (requires Hyper Backup package) |
| `reboot` | Graceful NAS reboot (prompts YES) |
| `shutdown` | Graceful NAS shutdown (prompts YES) |

### Packages
| Command | Description |
|---|---|
| `packages [filter]` | List installed packages; optional name filter |
| `install <name>` | Search Package Center catalog (111 packages) and install |
| `upgrade [package-id]` | List upgradeable packages or upgrade a specific one |

### DSM
| Command | Description |
|---|---|
| `dsm check` | Current DSM version, update availability, auto-upgrade setting |
| `dsm upgrade` | Download and install DSM update via SSH `synoupgrade` (prompts YES; reboots NAS) |

### Docker — HTTP API
| Command | Description |
|---|---|
| `docker list` | All containers with status, health, and image |
| `docker start <name>` | Start a stopped container |
| `docker stop <name>` | Stop a running container (prompts YES) |
| `docker restart <name>` | Restart a container (prompts YES) |
| `docker logs <name> [--lines N]` | Container logs — HTTP API with SSH fallback for Compose containers |
| `docker pull [<image:tag>]` | List local images; pull via SSH when image specified (prompts YES) |

### Docker — SSH (Compose stacks)
| Command | Description |
|---|---|
| `docker compose <path> <action>` | Run compose `up/down/pull/logs/ps/restart` in a directory |

### Deployment
| Command | Description |
|---|---|
| `deploy <repo-url> <path>` | Clone repo, bootstrap `.env`, run `docker compose up -d` |
| `deploy <path> --update` | Pull latest commits + `docker compose up -d` |
| `edit-env <path> <KEY=VALUE> ...` | Set .env keys via SFTP — values never in shell history |
| `setup-deploy-key` | Generate SSH deploy key on NAS for GitHub (run once) |
| `add-deploy-key <owner/repo>` | Register NAS deploy key on a GitHub repo via `gh` CLI |

### Files & Shell
| Command | Description |
|---|---|
| `file read <path>` | Print file contents (SFTP; falls back to sudo cat) |
| `file list <path>` | List directory (`ls -lh`) |
| `file exists <path>` | Check if file/directory exists |
| `file delete <path>` | Delete a file (prompts YES) |
| `ssh "<command>" [--sudo]` | Run an arbitrary shell command on the NAS |

## Architecture

```
skills/synology.py       ← single dispatcher, routes all subcommands
skills/*.py              ← individual skill modules
lib/auth.py              ← HTTP API session (SID token, POST-based)
lib/ssh.py               ← SSH client (paramiko, PTY sudo, stdin file writes)
```

**Two transport layers:**
- **HTTP API** (`lib/auth.py`) — DSM web API on port 5000/5001. Used for read operations, package management, container control.
- **SSH** (`lib/ssh.py`) — paramiko on port 2222. Used for git/deploy operations, docker compose, file management, and as fallback when HTTP API methods are missing or broken in Container Manager 24.x.

## Private GitHub Repos

SSH deploy keys are used — no tokens in config files or shell history.

```bash
# One-time NAS setup (generates the key, run once)
python skills/synology.py setup-deploy-key

# Per-repo: register the NAS key on GitHub (replaces manual GitHub UI steps)
python skills/synology.py add-deploy-key owner/repo

# Deploy
python skills/synology.py deploy git@github.com:owner/repo.git /volume1/docker/repo

# Update later
python skills/synology.py deploy /volume1/docker/repo --update
```

## Testing

```bash
# Unit tests (no NAS required)
python tests/test_unit.py

# HTTP API integration tests (live NAS)
python tests/integration.py

# SSH integration tests (live NAS)
python tests/test_ssh_integration.py
```

Current status: **29/29 unit** · **20/20 HTTP integration** · **23/23 SSH integration**

## Known Limitations

| Issue | Status |
|---|---|
| `docker compose logs` truncates at 120s | PTY timeout — use `docker logs` for single containers |
| Premium/hardware packages may not install via API | Use DSM UI |

## Tested Against

DS916+, DSM 7.2.2, Container Manager 24.x

---
**Publisher:** Xity Software, LLC
