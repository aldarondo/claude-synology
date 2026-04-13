"""
/synology-docker-pull <image:tag> — Pull or update a Docker image.
API: SYNO.Docker.Image
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def pull_image(host, sid, image):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Image",
            "version": "1",
            "method": "pull",
            "repository": f'"{image}"',
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: docker_pull.py <image:tag>")
        sys.exit(1)
    image = sys.argv[1]
    host, sid = get_session()
    try:
        result = pull_image(host, sid, image)
        if result.get("success"):
            print(f"Pull started: {image}")
        else:
            print(f"Failed: {result.get('error')}")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
