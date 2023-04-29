#!/bin/python3

import os
import re
import sys
import shlex
import subprocess
import argparse
from shutil import copyfile, rmtree

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

    prompt_key("Upload wheel and in-toto metadata to RSTUF [Alice]")
    os.chdir("../dist")
    print("TODO")

    prompt_key("Download and verify wheel [Client]")
    os.chdir("../client")
    print("TODO")

    # ====================================================================
    # Make changes
    # ====================================================================
    
    # TODO: clean project directory

    prompt_key("Setup layout to make changes [Alice]")
    os.chdir("../layouts")
    show_change_project_layout_cmd = "more change_project_layout.toml"
    print(show_change_project_layout_cmd)
    subprocess.call(shlex.split(show_change_project_layout_cmd))
    generate_change_layout_cmd = (
            "in-toto-layout-gen --signer ../private_keys/alice "
            "change_project_layout.toml")
    print(generate_change_layout_cmd)
    subprocess.call(shlex.split(generate_change_layout_cmd))

    prompt_key("Pull project [Bob]")
    os.chdir("../test-project")
    clone_project_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name clone "
        "--key ../private_keys/bob -p pyproject.toml README.md src "
        "--metadata-directory ../dist --no-command")
    print(clone_project_in_toto_run_cmd)
    subprocess.call(shlex.split(clone_project_in_toto_run_cmd))

    prompt_key("Make changes [Bob]")
    print("TODO")

    prompt_key("Build and upload wheel and metadata [Alice]")
    build_project_bob_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name build "
        "--key ../private_keys/bob -m pyproject.toml README.md src "
        "-p test_project-0.0.1-py3-none-any.whl --metadata-directory ../dist "
        "-- python3 -m build --wheel --outdir .")
    print(build_project_bob_in_toto_run_cmd)
    subprocess.call(shlex.split(build_project_bob_in_toto_run_cmd))
    os.chdir("../dist")

    prompt_key("Download and verify updated wheel [Client]")
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
        print("LOTS TODO")
        sys.exit(0)

    if args.no_prompt:
        global NO_PROMPT
        NO_PROMPT = True

    supply_chain()


if __name__ == '__main__':
    main()
