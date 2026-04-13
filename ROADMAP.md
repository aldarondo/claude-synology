# claude-synology Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🔄 In Progress
- [ ] `[Code]` Register skills in `~/.claude/` so they're invocable as `/synology-*` slash commands

## 🔲 Backlog

### Remaining Skills (stubs written, need testing/polish)
- [ ] `[Code]` `/synology-upgrade-package` — upgrade one or all outdated packages
- [ ] `[Code]` `/synology-install-package` — search Package Center and install
- [ ] `[Code]` `/synology-dsm-upgrade` — trigger DSM upgrade with confirmation gate
- [ ] `[Code]` `/synology-docker-start` — start a stopped container by name
- [ ] `[Code]` `/synology-docker-stop` — stop a running container by name
- [ ] `[Code]` `/synology-docker-logs` — tail recent logs from a container
- [ ] `[Code]` `/synology-docker-pull` — pull/update an image

### Known Limitations
- [ ] `[Human]` DSM update check (SYNO.Core.Upgrade.Server) returns error 103 — may need HTTPS port 5001 or different admin permissions. Investigate.
- [ ] `[Code]` Hyper Backup not installed — backup_status falls back to config backup only

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
- 2026-04-13 `[Code]` `/synology-dsm-check` — shows installed version + auto-upgrade setting

## 🚫 Blocked
<!-- log blockers here -->

## ✅ Completed
<!-- dated entries go here -->

## 🚫 Blocked
<!-- log blockers here -->
