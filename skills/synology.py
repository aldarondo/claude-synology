"""
Central dispatcher for all Synology NAS skills.

Usage:
  synology.py <command> [args...]
  synology.py              (shows help)

Commands:
  status                            System dashboard (CPU, RAM, temp, network, disk I/O)
  health                            Aggregated health check — storage, temps, containers, DSM
  storage                           Volume usage, RAID pools, disk health
  network                           Network interfaces, IPs, gateway
  logs [--level L] [--lines N]      System log viewer
  users                             NAS users and groups
  backup                            Hyper Backup task status
  reboot                            Reboot the NAS (prompts YES)
  shutdown                          Shut down the NAS (prompts YES)

  file read <path>                  SFTP: print file contents
  file list <path>                  SFTP: list directory
  file exists <path>                SFTP: check if file/dir exists
  file delete <path>                SSH: delete a file (prompts YES)

  packages [filter]                 List installed packages (optional name filter)
  install <package-id>              Install a package
  upgrade [package-id]              List upgradeable packages or upgrade one

  dsm check                         DSM version and update check
  dsm upgrade                       Trigger DSM upgrade (prompts confirmation)

  docker list                       List containers with status and health
  docker start <name>               Start a stopped container
  docker stop <name>                Stop a running container (prompts YES)
  docker restart <name>             Restart a running container (prompts YES)
  docker logs <name>                View container logs
  docker pull [name]                List images or pull a new one
  docker compose <path> <action>    SSH: compose up/down/pull/logs/ps/restart

  deploy <repo-url> <path>          SSH: clone repo + bootstrap .env + compose up
  deploy <path> --update            SSH: git pull + compose up
  edit-env <path> <KEY=VALUE> ...   SSH: set keys in a .env file (secrets-safe)
  ssh "<command>" [--sudo]          SSH: run a shell command on the NAS
  setup-deploy-key                  SSH: generate GitHub deploy key on NAS (run once)
"""

import sys
import os

# Ensure lib/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


HELP = __doc__.strip()


def dispatch(args):
    if not args:
        print(HELP)
        return

    cmd = args[0].lower()
    rest = args[1:]

    # ── Simple single-word commands ──────────────────────────────────────────
    if cmd == "status":
        from skills import status
        sys.argv = ["status.py"] + rest
        status.main()

    elif cmd == "storage":
        from skills import storage
        sys.argv = ["storage.py"] + rest
        storage.main()

    elif cmd == "logs":
        from skills import logs
        sys.argv = ["logs.py"] + rest
        logs.main()

    elif cmd == "users":
        from skills import users
        sys.argv = ["users.py"] + rest
        users.main()

    elif cmd == "backup":
        from skills import backup_status
        sys.argv = ["backup_status.py"] + rest
        backup_status.main()

    elif cmd == "health":
        from skills import health
        sys.argv = ["health.py"] + rest
        health.main()

    elif cmd == "network":
        from skills import network
        sys.argv = ["network.py"] + rest
        network.main()

    elif cmd == "reboot":
        from skills import reboot
        sys.argv = ["reboot.py"] + rest
        reboot.main()

    elif cmd == "shutdown":
        from skills import shutdown
        sys.argv = ["shutdown.py"] + rest
        shutdown.main()

    elif cmd == "edit-env":
        from skills import edit_env
        sys.argv = ["edit_env.py"] + rest
        edit_env.main()

    elif cmd == "file":
        from skills import file_ops
        sys.argv = ["file_ops.py"] + rest
        file_ops.main()

    elif cmd == "packages":
        from skills import packages
        sys.argv = ["packages.py"] + rest
        packages.main()

    elif cmd == "install":
        from skills import install_package
        sys.argv = ["install_package.py"] + rest
        install_package.main()

    elif cmd == "upgrade":
        from skills import upgrade_package
        sys.argv = ["upgrade_package.py"] + rest
        upgrade_package.main()

    elif cmd == "setup-deploy-key":
        from skills import setup_deploy_key
        sys.argv = ["setup_deploy_key.py"] + rest
        setup_deploy_key.main()

    elif cmd == "deploy":
        from skills import deploy
        sys.argv = ["deploy.py"] + rest
        deploy.main()

    elif cmd == "ssh":
        from skills import ssh_shell
        sys.argv = ["ssh_shell.py"] + rest
        ssh_shell.main()

    # ── dsm <subcommand> ─────────────────────────────────────────────────────
    elif cmd == "dsm":
        if not rest:
            print("Usage: synology dsm <check|upgrade>")
            sys.exit(1)
        sub = rest[0].lower()
        if sub == "check":
            from skills import dsm_check
            sys.argv = ["dsm_check.py"] + rest[1:]
            dsm_check.main()
        elif sub == "upgrade":
            from skills import dsm_upgrade
            sys.argv = ["dsm_upgrade.py"] + rest[1:]
            dsm_upgrade.main()
        else:
            die(f"Unknown dsm subcommand: {sub}\nUsage: synology dsm <check|upgrade>")

    # ── docker <subcommand> ──────────────────────────────────────────────────
    elif cmd == "docker":
        if not rest:
            print("Usage: synology docker <list|start|stop|logs|pull|compose>")
            sys.exit(1)
        sub = rest[0].lower()
        if sub == "list":
            from skills import docker
            sys.argv = ["docker.py"] + rest[1:]
            docker.main()
        elif sub == "start":
            from skills import docker_start
            sys.argv = ["docker_start.py"] + rest[1:]
            docker_start.main()
        elif sub == "stop":
            from skills import docker_stop
            sys.argv = ["docker_stop.py"] + rest[1:]
            docker_stop.main()
        elif sub == "logs":
            from skills import docker_logs
            sys.argv = ["docker_logs.py"] + rest[1:]
            docker_logs.main()
        elif sub == "pull":
            from skills import docker_pull
            sys.argv = ["docker_pull.py"] + rest[1:]
            docker_pull.main()
        elif sub == "restart":
            from skills import docker_restart
            sys.argv = ["docker_restart.py"] + rest[1:]
            docker_restart.main()
        elif sub == "compose":
            from skills import docker_compose
            sys.argv = ["docker_compose.py"] + rest[1:]
            docker_compose.main()
        else:
            die(f"Unknown docker subcommand: {sub}\n"
                "Usage: synology docker <list|start|stop|restart|logs|pull|compose>")

    # ── unknown ──────────────────────────────────────────────────────────────
    else:
        print(f"Unknown command: {cmd}\n")
        print(HELP)
        sys.exit(1)


def main():
    dispatch(sys.argv[1:])


if __name__ == "__main__":
    main()
