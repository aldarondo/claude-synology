"""
/synology-docker-pull <image:tag> — List local images or pull a new one.
API: SYNO.Docker.Image v1

Usage:
  docker_pull.py                     List all local images
  docker_pull.py <image:tag>         Pull/update an image from Docker Hub
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from lib.auth import get_session, logout


def list_images(host, sid):
    resp = requests.get(
        f"{host}/webapi/entry.cgi",
        params={
            "api": "SYNO.Docker.Image",
            "version": "1",
            "method": "list",
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def pull_image(host, sid, image, tag="latest"):
    # Synology Container Manager pull via POST with JSON body
    resp = requests.post(
        f"{host}/webapi/entry.cgi",
        data={
            "api": "SYNO.Docker.Image",
            "version": "1",
            "method": "pull",
            "repository": image,
            "tag": tag,
            "_sid": sid,
        },
        verify=False,
    )
    return resp.json()


def main():
    host, sid = get_session()
    try:
        if len(sys.argv) < 2:
            # List local images
            data = list_images(host, sid)
            if data.get("success"):
                images = data.get("data", {}).get("images", [])
                print(f"=== Local Docker Images ({len(images)}) ===\n")
                print(f"  {'REPOSITORY':<45} {'TAG':<20} SIZE")
                print("  " + "-" * 75)
                for img in sorted(images, key=lambda x: x.get("repository", "")):
                    repo = img.get("repository", "?")
                    tag  = img.get("tag", "?")
                    size = img.get("size", 0)
                    size_mb = f"{size / 1024 ** 2:.0f} MB" if size else "?"
                    print(f"  {repo:<45} {tag:<20} {size_mb}")
            else:
                code = data.get("error", {}).get("code", "?")
                print(f"Could not list images (error {code}).")
            return

        # Pull an image
        image_arg = sys.argv[1]
        if ":" in image_arg:
            repo, tag = image_arg.rsplit(":", 1)
        else:
            repo, tag = image_arg, "latest"

        print(f"Pulling {repo}:{tag} ...")
        result = pull_image(host, sid, repo, tag)
        if result.get("success"):
            print(f"Pull started: {repo}:{tag}")
            print("Check Container Manager > Image for progress.")
        else:
            code = result.get("error", {}).get("code", "?")
            print(f"Pull failed (error {code}).")
            print("You can pull images manually in DSM > Container Manager > Image > Add > Add from URL.")
    finally:
        logout(host, sid)


if __name__ == "__main__":
    main()
