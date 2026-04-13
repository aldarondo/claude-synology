# claude-synology Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🔄 In Progress

## 🔲 Backlog

### Known Limitations
- [ ] `[Human]` Hyper Backup not installed — install from Package Center to enable `/synology-backup-status`
- [ ] `[Code]` Docker logs (error 114) — DSM Container Manager 24.x does not expose log streaming via HTTP API for Compose containers; view logs in DSM UI instead

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
- 2026-04-13 `[Code]` `/synology-dsm-upgrade` — checks for update first, requires YES confirmation, warns about NAS reboot

## 🚫 Blocked
<!-- log blockers here -->
