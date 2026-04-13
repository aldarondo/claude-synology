# claude-synology Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🔄 In Progress
- [ ] `[Code]` Define project game plan

## 🔲 Backlog

### Setup
- [ ] `[Human]` Provide NAS IP, admin credentials, confirm DSM API access is enabled in Control Panel
- [ ] `[Code]` Implement `lib/auth.py` — SID session login/logout, load config from `config.json`
- [ ] `[Code]` Create `config.example.json` template
- [ ] `[Code]` Implement `/synology-status` as first working skill (proves auth end-to-end)

### Package Management
- [ ] `[Code]` `/synology-packages` — list installed packages, flag outdated
- [ ] `[Code]` `/synology-upgrade-package` — upgrade one or all outdated packages
- [ ] `[Code]` `/synology-install-package` — search Package Center and install

### DSM Updates
- [ ] `[Code]` `/synology-dsm-check` — current version + available update info
- [ ] `[Code]` `/synology-dsm-upgrade` — trigger DSM upgrade with confirmation gate

### Docker / Container Manager
- [ ] `[Code]` `/synology-docker` — list all containers with status, image, uptime
- [ ] `[Code]` `/synology-docker-start` — start a stopped container by name
- [ ] `[Code]` `/synology-docker-stop` — stop a running container by name
- [ ] `[Code]` `/synology-docker-logs` — tail recent logs from a container
- [ ] `[Code]` `/synology-docker-pull` — pull/update an image

### Storage & Health
- [ ] `[Code]` `/synology-storage` — volume health, RAID status, S.M.A.R.T summary
- [ ] `[Code]` `/synology-logs` — system and security log viewer, filter by severity
- [ ] `[Code]` `/synology-backup-status` — Hyper Backup job status (last run, next run, result)

### User Management
- [ ] `[Code]` `/synology-users` — list users and group memberships

### Skill Registration
- [ ] `[Code]` Register all skills in `~/.claude/skills/` so they're invocable from any session

## ✅ Completed
<!-- dated entries go here -->

## 🚫 Blocked
<!-- log blockers here -->
