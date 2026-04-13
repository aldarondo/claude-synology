# claude-synology

Manage a Synology NAS from Claude Code via Python scripts — packages, DSM updates, Docker containers, storage health, users, and logs.

## Features
- System dashboard: CPU, RAM, temp, uptime, network, disk I/O
- List installed packages (38 on DS916+)
- Check DSM version and available updates
- Docker container management (list, start, stop, pull, logs)
- Storage: volume usage, RAID pool status, disk S.M.A.R.T and temps
- System log viewer with level/type filters
- User and group listing

## Tech Stack
| Layer | Technology |
|---|---|
| Language | Python 3 |
| API | Synology DSM HTTP API (session-based, port 5000) |
| Auth | `lib/auth.py` — POST-based SID token, auto-corrects protocol |
| Interface | `python skills/<skill>.py` |

## Skills

### Working
| Script | Description |
|---|---|
| `skills/status.py` | System dashboard — model, DSM version, CPU, RAM, temp, network, disk I/O |
| `skills/packages.py` | List all installed packages; `--filter <text>` to narrow |
| `skills/dsm_check.py` | Current DSM version, live update check, auto-upgrade setting |
| `skills/docker.py` | List containers with status, health, and image |
| `skills/storage.py` | Volume usage bars, RAID pool table, disk temps and S.M.A.R.T |
| `skills/logs.py` | System logs; `--level error|warning|info` `--lines N` filters |
| `skills/users.py` | All NAS users with email and group memberships |
| `skills/backup_status.py` | Hyper Backup task status (requires Hyper Backup package) |

### Stubs (written, not yet tested)
| Script | Description |
|---|---|
| `skills/upgrade_package.py` | Upgrade a specific package or all outdated ones |
| `skills/install_package.py` | Search Package Center and install a package |
| `skills/dsm_upgrade.py` | Trigger DSM upgrade with confirmation gate |
| `skills/docker_start.py` | Start a stopped container |
| `skills/docker_stop.py` | Stop a running container |
| `skills/docker_logs.py` | Tail recent logs from a container |
| `skills/docker_pull.py` | Pull or update a Docker image |

## Getting Started

1. Copy `config.example.json` to `config.json` and fill in your NAS IP and credentials.
2. `config.json` is gitignored — never commit it.
3. Install dependencies:

```bash
pip install requests
```

4. Test auth:

```bash
python lib/auth.py
```

## Configuration

```json
{
  "host": "http://192.168.x.x:5000",
  "username": "admin",
  "password": "your-password",
  "verify_ssl": false
}
```

Port notes: `5000` = HTTP, `5001` = HTTPS. `lib/auth.py` auto-corrects if you mix them up.

## Project Status
Core read skills working against a DS916+ running DSM 7.2.2. Write operations (upgrade, install, start/stop) scaffolded but not yet validated. See [ROADMAP.md](ROADMAP.md).

---
**Publisher:** Xity Software, LLC
