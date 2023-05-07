#!/bin/python3

import os
import re
import sys
import shlex
import subprocess
import argparse
from shutil import copyfile, rmtree
import hashlib
import binascii
import requests

NO_PROMPT = False
TESTREPO = "alanssitis/test-project"


def prompt_key(prompt):
    if NO_PROMPT:
        print("\n" + prompt)
        return
    inp = False
    while inp != "":
        try:
            inp = input("\n{} -- press any key to continue".format(prompt))
        except Exception:
            pass


def supply_chain():
    if not os.path.exists("dist"):
        os.mkdir("dist")
    if not os.path.exists("client"):
        os.mkdir("client")
    copyfile("layouts/keys/alice.pub", "dist/alice.pub")

    # ====================================================================
    # Start project
    # ====================================================================

    prompt_key("Define the supply chain layout [Alice]")
    os.chdir("layouts")
    show_new_project_layout_cmd = "more new_project_layout.toml"
    print(show_new_project_layout_cmd)
    subprocess.call(shlex.split(show_new_project_layout_cmd))

    prompt_key("Generate signed layout [Alice]")
    generate_new_layout_cmd = (
        "in-toto-layout-gen --signer ../private_keys/alice "
        "new_project_layout.toml")
    print(generate_new_layout_cmd)
    subprocess.call(shlex.split(generate_new_layout_cmd))
    copy_layout_to_dist_cmd = "mv root.layout ../dist"
    print(copy_layout_to_dist_cmd)
    subprocess.call(shlex.split(copy_layout_to_dist_cmd))

    prompt_key("Create project [Alice]")
    os.chdir("../test-project")
    create_project_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name create "
        "--key ../private_keys/alice -p pyproject.toml README.md src "
        "--metadata-directory ../dist --no-command")
    print(create_project_in_toto_run_cmd)
    subprocess.call(shlex.split(create_project_in_toto_run_cmd))

    prompt_key("Build project [Alice]")
    build_project_alice_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name build "
        "--key ../private_keys/alice -m pyproject.toml README.md src "
        "-p test_project-0.0.1-py3-none-any.whl --metadata-directory ../dist "
        "-- python3 -m build --wheel --outdir .")
    print(build_project_alice_in_toto_run_cmd)
    subprocess.call(shlex.split(build_project_alice_in_toto_run_cmd))
    mv_project_cmd = "mv test_project-0.0.1-py3-none-any.whl ../dist"
    print(mv_project_cmd)
    subprocess.call(shlex.split(mv_project_cmd))

    prompt_key("Upload wheel and in-toto metadata to RSTUF [Alice]")
    os.chdir("../dist")
    print("TODO")

    prompt_key("Download and verify wheel [Client]")
    # Needs to be moved to "client side"
    subprocess.call(
        shlex.split(
            "in-toto-verify --verbose --layout root.layout --layout-keys alice.pub"
        ))
    os.chdir("../client")
    print("TODO WITH RSTUF impl")

    prompt_key("Clear /dist and /client")
    os.chdir("..")
    clear_dist_cmd = "rm -rf dist"
    print(clear_dist_cmd)
    subprocess.call(shlex.split(clear_dist_cmd))
    clear_client_cmd = "rm -rf client"
    print(clear_client_cmd)
    subprocess.call(shlex.split(clear_client_cmd))

    if not os.path.exists("dist"):
        os.mkdir("dist")
    if not os.path.exists("client"):
        os.mkdir("client")
    copyfile("layouts/keys/alice.pub", "dist/alice.pub")
    copyfile("layouts/keys/bob.pub", "dist/bob.pub")

    # ====================================================================
    # Make changes
    # ====================================================================

    prompt_key("Setup layout to make changes [Alice]")
    os.chdir("layouts")
    show_change_project_layout_cmd = "more change_project_layout.toml"
    print(show_change_project_layout_cmd)
    subprocess.call(shlex.split(show_change_project_layout_cmd))
    generate_change_layout_cmd = (
        "in-toto-layout-gen --signer ../private_keys/alice "
        "change_project_layout.toml")
    print(generate_change_layout_cmd)
    subprocess.call(shlex.split(generate_change_layout_cmd))
    print(copy_layout_to_dist_cmd)
    subprocess.call(shlex.split(copy_layout_to_dist_cmd))

    prompt_key("Pull project [Bob]")
    os.chdir("../test-project")
    clone_project_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name clone "
        "--key ../private_keys/bob -p pyproject.toml README.md src "
        "--metadata-directory ../dist --no-command")
    print(clone_project_in_toto_run_cmd)
    subprocess.call(shlex.split(clone_project_in_toto_run_cmd))

    prompt_key("Make changes [Bob]")

    in_toto_record_start_bob_changes_cmd = (
        "in-toto-record start --verbose --step-name update "
        "--key ../private_keys/bob -m pyproject.toml README.md src")
    print(in_toto_record_start_bob_changes_cmd)
    subprocess.call(shlex.split(in_toto_record_start_bob_changes_cmd))

    print("Copying pre-created files to project")
    copyfile("../project_files/pyproject.toml.changed", "pyproject.toml")
    copyfile("../project_files/main.py.changed", "src/main.py")

    in_toto_record_stop_bob_changes_cmd = (
        "in-toto-record stop --verbose --step-name update "
        "--key ../private_keys/bob -p pyproject.toml README.md src")
    print(in_toto_record_stop_bob_changes_cmd)
    subprocess.call(shlex.split(in_toto_record_stop_bob_changes_cmd))

    mv_update_link_cmd = "mv update.776a00e2.link ../dist"
    print(mv_update_link_cmd)
    subprocess.call(shlex.split(mv_update_link_cmd))

    prompt_key("Build and upload wheel and metadata [Alice]")
    build_project_alice_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name build "
        "--key ../private_keys/alice -m pyproject.toml README.md src "
        "-p test_project-0.0.2-py3-none-any.whl --metadata-directory ../dist "
        "-- python3 -m build --wheel --outdir .")
    print(build_project_alice_in_toto_run_cmd)
    subprocess.call(shlex.split(build_project_alice_in_toto_run_cmd))
    mv_project_cmd = "mv test_project-0.0.2-py3-none-any.whl ../dist"
    print(mv_project_cmd)
    subprocess.call(shlex.split(mv_project_cmd))
    os.chdir("../dist")
    print("Start a HTTP server to host the wheel and in-toto metadata")
    start_server_cmd = "gnome-terminal -- python3 -m http.server"
    subprocess.Popen(shlex.split(start_server_cmd))

    # Calculate targets' length and b2sum
    root_layout_path = 'root.layout'
    alice_pub_path = 'alice.pub'
    build_link_path = 'build.556caebd.link'
    create_link_path = 'create.556caebd.link'
    wheel_path = 'test_project-0.0.1-py3-none-any.whl'

    with open(root_layout_path, 'rb') as f:
        hash_root_layout = hashlib.blake2b(digest_size=32)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_root_layout.update(chunk)
    root_layout_bytes = hash_root_layout.digest()
    root_layout_b2sum = binascii.hexlify(root_layout_bytes).decode('utf-8')
    root_layout_length = os.path.getsize(root_layout_path)

    with open(alice_pub_path, 'rb') as f:
        hash_alice_pub = hashlib.blake2b(digest_size=32)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_alice_pub.update(chunk)
    alice_pub_bytes = hash_alice_pub.digest()
    alice_pub_b2sum = binascii.hexlify(alice_pub_bytes).decode('utf-8')
    alice_pub_length = os.path.getsize(alice_pub_path)

    with open(build_link_path, 'rb') as f:
        hash_build_link = hashlib.blake2b(digest_size=32)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_build_link.update(chunk)
    build_link_bytes = hash_build_link.digest()
    build_link_b2sum = binascii.hexlify(build_link_bytes).decode('utf-8')
    build_link_length = os.path.getsize(build_link_path)

    with open(create_link_path, 'rb') as f:
        hash_create_link = hashlib.blake2b(digest_size=32)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_create_link.update(chunk)
    create_link_bytes = hash_create_link.digest()
    create_link_b2sum = binascii.hexlify(create_link_bytes).decode('utf-8')
    create_link_length = os.path.getsize(create_link_path)

    with open(wheel_path, 'rb') as f:
        hash_wheel = hashlib.blake2b(digest_size=32)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_wheel.update(chunk)
    wheel_bytes = hash_wheel.digest()
    wheel_b2sum = binascii.hexlify(wheel_bytes).decode('utf-8')
    wheel_length = os.path.getsize(wheel_path)

    post_target_url = 'http://localhost:80/api/v1/targets/'
    post_target_body = {
        "targets": [
            {
            "info": {
                "length": root_layout_length,
                "hashes": {
                    "blake2b-256": root_layout_b2sum
                }
            },
            "path": root_layout_path
            },
            {
            "info": {
                "length": alice_pub_length,
                "hashes": {
                    "blake2b-256": alice_pub_b2sum
                }
            },
            "path": alice_pub_path
            },
            {
            "info": {
                "length": build_link_length,
                "hashes": {
                    "blake2b-256": build_link_b2sum
                }
            },
            "path": build_link_path
            },
            {
            "info": {
                "length": create_link_length,
                "hashes": {
                    "blake2b-256": create_link_b2sum
                }
            },
            "path": create_link_path
            },
            {
            "info": {
                "length": wheel_length,
                "hashes": {
                    "blake2b-256": wheel_b2sum
                }
            },
            "path": wheel_path
            }
        ]
    }

    print("Uploading targets to rstuf...")
    post_target_request = requests.post(post_target_url, json = post_target_body)
    print(post_target_request.text)

    prompt_key("Download and verify updated wheel [Client]")
    # Needs to be moved to "client side"
    subprocess.call(
        shlex.split(
            "in-toto-verify --verbose --layout root.layout --layout-keys alice.pub"
        ))
    os.chdir("../client")
    print("TODO")

    # ====================================================================
    # Compromise project
    # ====================================================================

    print("Adversary does not have Alice's private key")
    prompt_key("Tamper with source code [Adversary]")
    os.chdir("../test-project")
    print("TODO")

    prompt_key("Build and upload new wheel and update RSTUF [Adversary]")
    os.chdir("../dist")
    print("TODO")

    prompt_key("Download and verify compromised wheel [Client]")
    os.chdir("../client")
    print("TODO")


def extract_gh_repo(uri):
    ssh_pattern = r'^git@github.com:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+).git$'
    repo = re.findall(ssh_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    https_pattern = r'^https://github.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+).git$'
    repo = re.findall(https_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    regular_pattern = r'^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)$'
    repo = re.findall(regular_pattern, uri)
    if len(repo) > 0:
        return repo[0]
    sys.exit(f'failed to extract github repo from "{uri}"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n",
                        "--no-prompt",
                        help="No prompt.",
                        action="store_true")
    parser.add_argument("-c",
                        "--clean",
                        help="Remove files created during demo.",
                        action="store_true")
    args = parser.parse_args()

    if repo := os.getenv("TESTREPO"):
        global TESTREPO
        TESTREPO = extract_gh_repo(repo)
        print(TESTREPO)

    if args.clean:
        copyfile("project_files/pyproject.toml.original",
                 "test-project/pyproject.toml")
        copyfile("project_files/main.py.original", "test-project/src/main.py")
        sys.exit(0)

    if args.no_prompt:
        global NO_PROMPT
        NO_PROMPT = True

    supply_chain()


if __name__ == '__main__':
    main()
