# claude-synology

## Project Purpose
Manage a household Synology NAS from Claude Code via slash command skills — covering packages, DSM updates, Docker, storage, users, logs, and backups.

## Key Commands
```bash
# Test auth connection
python lib/auth.py

# Run a skill manually (example)
python skills/status.py
```

## Config
NAS connection lives in `config.json` (gitignored). Copy `config.example.json` to get started.

## Skill Files
Each skill in `skills/` is a standalone Python script. All use `lib/auth.py` for session management.

@~/Documents/GitHub/CLAUDE.md
