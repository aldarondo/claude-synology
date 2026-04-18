# claude-synology

## Project Purpose
Manage a household Synology NAS from Claude Code via slash command skills — covering packages, DSM updates, Docker, storage, users, logs, and backups.

## Key Commands
```bash
# Test HTTP API auth
python lib/auth.py

# Test SSH connection (also runs docker ps)
python lib/ssh.py

# Run a skill manually (example)
python skills/status.py

# Install dependencies
pip install -r requirements.txt
```

## Config
NAS connection lives in `config.json` (gitignored). Copy `config.example.json` to get started.
The `ssh` block in config.json is required for SSH-based skills (deploy, docker-compose, ssh-shell).

## Skill Files
Each skill in `skills/` is a standalone Python script.
- HTTP API skills use `lib/auth.py` for session management
- SSH skills use `lib/ssh.py` (paramiko, requires SSH enabled on NAS port 2222)

@~/Documents/GitHub/CLAUDE.md

## Git Rules
- Never create pull requests. Push directly to main.
- solo/auto-push OK
