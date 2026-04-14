# claude-synology Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🔄 In Progress

## 🔲 Backlog

### Cowork Research Tasks
- [ ] `[Cowork]` **Docker container logs** — `SYNO.Docker.Container.Log` returns error 114 for all Compose containers on Container Manager 24.x. Research: SSH-based `docker logs` access, Task Scheduler script workaround, syslog forwarding, or undocumented API paths in Container Manager 24.x that expose log streaming.
- [ ] `[Cowork]` **Docker image pull** — `SYNO.Docker.Image pull` method not found (error 103) via HTTP API on Container Manager 24.x. Research: correct API path/method for pulling images programmatically, or whether it was moved to a different namespace in Container Manager 24.x.
- [ ] `[Cowork]` **DSM upgrade trigger** — `SYNO.Core.Upgrade upgrade` method not found (error 103). Download step (`SYNO.Core.Upgrade.Server.Download v2 start`) exists but needs correct params (currently error 101 = invalid param). Research: correct two-step download+install flow and required parameters for triggering a DSM upgrade via the HTTP API.
- [ ] `[Cowork]` **Package install from catalog** — `SYNO.Core.Package.Installation install` returns error 120 for any package not pre-staged. Research: whether the Package Center catalog can be browsed and packages installed via API without a MyDS account session, or if there's a workaround using package feed URLs.

### Human Tasks
- [ ] `[Human]` Install Hyper Backup from Package Center (DSM UI) to enable `/synology-backup-status`
- [ ] `[Human]` Provide GitHub Personal Access Token for deploying private repos (needed for `/synology-deploy` with private repos)

## ✅ Completed
- 2026-04-13 `[Human]` Provide NAS IP, admin credentials, confirm DSM API access enabled
- 2026-04-13 `[Code]` Implement `lib/auth.py` — POST-based SID session, auto-fix https on port 5000
- 2026-04-13 `[Code]` Create `config.example.json` template
- 2026-04-13 `[Code]` `/synology-status` — DS916+, DSM version, CPU, RAM, temp, network, disk I/O
- 2026-04-13 `[Code]` `/synology-packages` — 38 packages listed, filterable by name
- 2026-04-13 `[Code]` `/synology-docker` — 2 containers (open-webui, ollama) with health status
- 2026-04-13 `[Code]` `/synology-storage` — 2 volumes, 2 RAID5 pools, 9 disks with temps and SMART
- 2026-04-13 `[Code]` `/synology-logs` — syslog with level/type filters
- 2026-04-13 `[Code]` `/synology-users` — 12 users listed
- 2026-04-13 `[Code]` `/synology-dsm-check` — shows installed version, live update check, auto-upgrade setting
- 2026-04-13 `[Code]` Register 16 commands in `~/.claude/commands/` — all read and write synology skills
- 2026-04-13 `[Code]` `/synology-docker-start` — verified working, guards against starting already-running containers
- 2026-04-13 `[Code]` `/synology-docker-stop` — verified working, requires YES confirmation
- 2026-04-13 `[Code]` `/synology-docker-logs` — graceful fallback (API unsupported for Compose containers)
- 2026-04-13 `[Code]` `/synology-docker-pull` — list local images; pull via API (fallback to UI instructions)
- 2026-04-13 `[Code]` `/synology-upgrade-package` — lists user packages; triggers upgrade with YES confirmation (error 4501 = already up to date)
- 2026-04-13 `[Code]` `/synology-install-package` — triggers install with YES confirmation; graceful fallback if package unavailable via API
- 2026-04-13 `[Code]` `/synology-dsm-upgrade` — checks for update first, requires YES confirmation, warns about NAS reboot (trigger method broken — Cowork task)
- 2026-04-13 `[Code]` `tests/integration.py` — 19/19 passing; covers all read APIs, write method existence, and documents 3 known-broken skips
- 2026-04-13 `[Code]` `/synology-docker-pull` — fixed image list (limit/offset), shows upgradable flag; pull remains UI-only (Cowork task)
- 2026-04-13 `[Code]` `/synology-install-package` — moved to Cowork research backlog
- 2026-04-13 `[Human]` Enable SSH on NAS (port 2222) — SSH layer now active
- 2026-04-13 `[Code]` `lib/ssh.py` — paramiko SSH client with PTY sudo support, password injection, ANSI cleanup; tested against live NAS
- 2026-04-13 `[Code]` `/synology-ssh` — arbitrary SSH shell commands with destructive-op confirmation gate
- 2026-04-13 `[Code]` `/synology-docker-compose` — SSH-based compose up/down/pull/logs/ps/restart; requires YES for destructive actions
- 2026-04-13 `[Code]` `/synology-deploy` — SSH-based git clone/pull + .env bootstrap + docker compose up -d; supports --token for private repos
- 2026-04-13 `[Code]` `requirements.txt` — added paramiko>=3.0, requests>=2.28
- 2026-04-13 `[Code]` Register 3 new SSH commands in ~/.claude/commands/ (synology-ssh, synology-docker-compose, synology-deploy)

## 🚫 Blocked
<!-- log blockers here -->
