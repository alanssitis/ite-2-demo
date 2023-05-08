#!/usr/bin/env python3
"""TUF Client Example"""

# Copyright 2012 - 2017, New York University and the TUF contributors
# SPDX-License-Identifier: MIT OR Apache-2.0

import argparse
import logging
import os
from shutil import move
import requests
import shlex
import subprocess
import sys
import tempfile
import traceback
from hashlib import sha256
from pathlib import Path

from tuf.api.exceptions import DownloadError, RepositoryError
from tuf.ngclient.config import UpdaterConfig
from tuf.ngclient.updater import Updater

import securesystemslib.hash

# constants
DOWNLOAD_DIR = "./"
CLIENT_EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
API_URL = "http://127.0.0.1:80/api/v1/targets/"
METADATA_URL = "http://127.0.0.1:8080/"
TARGET_URL = "http://127.0.0.1:8000/"
ADD_TARGET_TOKEN = os.environ["ADD_TARGET_TOKEN"]
DEL_TARGET_TOKEN = os.environ["DEL_TARGET_TOKEN"]


def build_metadata_dir(base_url: str) -> str:
    """build a unique and reproducible directory name for the repository url"""
    name = sha256(base_url.encode()).hexdigest()[:8]
    # TODO: Make this not windows hostile?
    return f"{Path.home()}/.local/share/tuf-example/{name}"


def download(target: str, skip_in_toto_verify: bool) -> bool:
    """
    Download the target file using ``ngclient`` Updater.

    The Updater refreshes the top-level metadata, get the target information,
    verifies if the target is already cached, and in case it is not cached,
    downloads the target file.

    Returns:
        A boolean indicating if process was successful
    """
    metadata_dir = build_metadata_dir(METADATA_URL)

    if not os.path.isfile(f"{metadata_dir}/root.json"):
        print("Download root metadata to "
              f"{metadata_dir}/root.json")
        return False

    print(f"Using trusted root in {metadata_dir}")

    if not os.path.isdir(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    try:
        with tempfile.TemporaryDirectory("in-toto-rstuf") as tmpdirname:
            updater = Updater(
                metadata_dir=metadata_dir,
                metadata_base_url=METADATA_URL,
                target_base_url=TARGET_URL,
                target_dir=tmpdirname,
                config=UpdaterConfig(prefix_targets_with_hash=False),
            )
            updater.refresh()

            if not download_file(updater, target):
                return True

            if not skip_in_toto_verify:
                cwd = os.getcwd()
                os.chdir(tmpdirname)
                cmd = ("in-toto-verify --verbose --layout root.layout "
                       "--layout-keys alice.pub")
                subprocess.check_output(shlex.split(cmd))
                os.chdir(cwd)

            dest = move(os.path.join(tmpdirname, target), DOWNLOAD_DIR)
            print(f"Target downloaded and available in {dest}")

    except (OSError, RepositoryError, DownloadError) as e:
        print(f"Failed to download target {target}: {e}")
        if logging.root.level < logging.ERROR:
            traceback.print_exc()
        return False

    return True


def download_file(updater, target):
    info = updater.get_targetinfo(target)

    if info is None:
        print(f"Target {target} not found")
        return False

    if info.custom and "in-toto" in info.custom:
        for f in info.custom["in-toto"]:
            if not download_file(updater, f):
                return False

    path = updater.find_cached_target(info)
    if path:
        print(f"Target is available in {path}")
        return True
    path = updater.download_target(info)
    return True


def add_target(filename, custom=None):
    info = {
        "length": os.path.getsize(filename),
        "hashes": {
            "blake2b-256":
            securesystemslib.hash.digest_filename(
                filename, algorithm="blake2b-256").hexdigest()
        }
    }
    if custom:
        info["custom"] = custom

    return {"path": filename, "info": info}


def upload_layout(layout, keys):
    targets = []

    try:
        targets.append(add_target(layout, {"in-toto": keys}))
        for k in keys:
            targets.append(add_target(k))
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {ADD_TARGET_TOKEN}",
            "Content-Type": "application/json",
        }
        r = requests.post(API_URL, headers=headers, json={"targets": targets})
        r.raise_for_status()
        print(f"Layout {layout} uploaded successfully along with metadata")

    except Exception as e:
        print(f"Failed to upload layout {layout}: {e}")
        if logging.root.level < logging.ERROR:
            traceback.print_exc()
        return False

    return True


def upload_file(target, layout, links):
    targets = []

    try:
        targets.append(add_target(target, {"in-toto": [layout] + links}))
        for l in links:
            targets.append(add_target(l))
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {ADD_TARGET_TOKEN}",
            "Content-Type": "application/json",
        }
        r = requests.post(API_URL, headers=headers, json={"targets": targets})
        r.raise_for_status()
        print(f"Target {target} uploaded successfully along with metadata")

    except Exception as e:
        print(f"Failed to upload target {target}: {e}")
        if logging.root.level < logging.ERROR:
            traceback.print_exc()
        return False

    return True


def delete(targets):
    try:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {DEL_TARGET_TOKEN}",
            "Content-Type": "application/json",
        }
        r = requests.delete(API_URL,
                            headers=headers,
                            json={"targets": targets})
        r.raise_for_status()
        print(f"Targets {targets} successfully deleted")

    except Exception as e:
        print(f"Failed to delete targets {targets}: {e}")
        if logging.root.level < logging.ERROR:
            traceback.print_exc()
        return False

    return True


def main():
    """Main TUF Client Example function"""

    client_args = argparse.ArgumentParser(description="TUF Client Example")

    # Global arguments
    client_args.add_argument(
        "-v",
        "--verbose",
        help="Output verbosity level (-v, -vv, ...)",
        action="count",
        default=0,
    )

    # Sub commands
    sub_command = client_args.add_subparsers(dest="sub_command")

    # Download
    download_parser = sub_command.add_parser(
        "download",
        help="Download a target file",
    )
    download_parser.add_argument(
        "target",
        metavar="TARGET",
        help="Target file",
    )
    download_parser.add_argument(
        "--skip-in-toto-verify",
        action="store_true",
        help="Force file to install without in-toto-verify",
    )

    # Upload layout
    upload_layout_parser = sub_command.add_parser(
        "upload-layout",
        help="Upload in-toto layout",
    )
    upload_layout_parser.add_argument(
        "layout",
        metavar="LAYOUT",
        help="Root in-toto layout",
    )
    upload_layout_parser.add_argument(
        "keys",
        metavar="KEYS",
        nargs='+',
        help="Public keys for layout",
    )

    # Upload file
    upload_file_parser = sub_command.add_parser(
        "upload-file",
        help="Upload a target file with in-toto metadata",
    )
    upload_file_parser.add_argument(
        "target",
        metavar="TARGET",
        help="Target file",
    )
    upload_file_parser.add_argument(
        "layout",
        metavar="LAYOUT",
        help="Target layout",
    )
    upload_file_parser.add_argument(
        "links",
        metavar="LINKS",
        nargs='+',
        help="in-toto link metadata of TARGET",
    )

    # Delete targets
    delete_parser = sub_command.add_parser(
        "delete",
        help="Delete RSTUF entries",
    )
    delete_parser.add_argument(
        "targets",
        metavar="TARGETS",
        nargs='+',
        help="RSTUF targets to delete",
    )

    command_args = client_args.parse_args()

    if command_args.verbose == 0:
        loglevel = logging.ERROR
    elif command_args.verbose == 1:
        loglevel = logging.WARNING
    elif command_args.verbose == 2:
        loglevel = logging.INFO
    else:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)

    # initialize the TUF Client Example infrastructure
    if command_args.sub_command == "download":
        if not download(command_args.target, command_args.skip_in_toto_verify):
            return f"Failed to download {command_args.target}"
    elif command_args.sub_command == "upload-layout":
        if not upload_layout(command_args.layout, command_args.keys):
            return f"Failed to upload layout {command_args.layout}"
    elif command_args.sub_command == "upload-file":
        if not upload_file(command_args.target, command_args.layout,
                           command_args.links):
            return f"Failed to upload target {command_args.target}"
    elif command_args.sub_command == "delete":
        if not delete(command_args.targets):
            return f"Failed to delete targets"
    else:
        client_args.print_help()


if __name__ == "__main__":
    sys.exit(main())
