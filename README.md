# claude-synology

Manage a Synology NAS from Claude Code via slash commands — packages, DSM updates, Docker containers, storage health, users, logs, and backups.

## Features
- Check system status (CPU, RAM, temps, disk usage)
- List, install, and upgrade packages via Package Center
- Check and apply DSM updates
- Manage Docker containers (list, start, stop, pull, logs)
- Monitor storage volumes and disk S.M.A.R.T health
- Browse system and security logs
- View Hyper Backup job status

## Tech Stack
| Layer | Technology |
|---|---|
| Language | Python 3 |
| API | Synology DSM HTTP API (session-based) |
| Auth | `lib/auth.py` — SID token management |
| Interface | Claude Code slash command skills |

## Skills

| Skill | Description |
|---|---|
| `/synology-status` | System dashboard — CPU, RAM, temps, uptime, disk usage |
| `/synology-packages` | List installed packages, flag outdated ones |
| `/synology-upgrade-package` | Upgrade a specific package or all outdated ones |
| `/synology-install-package` | Search Package Center and install a new package |
| `/synology-dsm-check` | Check current DSM version + available update |
| `/synology-dsm-upgrade` | Trigger DSM upgrade (with confirmation prompt) |
| `/synology-docker` | List containers — status, image, uptime |
| `/synology-docker-start` | Start a stopped container |
| `/synology-docker-stop` | Stop a running container |
| `/synology-docker-logs` | Tail logs from a container |
| `/synology-docker-pull` | Pull a new image or update an existing one |
| `/synology-storage` | Volume health, RAID status, disk S.M.A.R.T summary |
| `/synology-logs` | Recent system/security logs, filter by severity |
| `/synology-users` | List users and groups |
| `/synology-backup-status` | Hyper Backup job status — last run, next run, result |

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
  "password": "your-password"
}
```

## Project Status
Early development. See [ROADMAP.md](ROADMAP.md) for what's planned.

---
**Publisher:** Xity Software, LLC
