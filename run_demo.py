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
    # ====================================================================
    # Tampering with the supply chain
    # ====================================================================

    prompt_key("Define the supply chain layout [Alice]")
    os.chdir("dist")
    show_new_project_layout_cmd = "less new_project_layout.toml"
    print(show_new_project_layout_cmd)
    subprocess.call(shlex.split(show_new_project_layout_cmd))

    prompt_key("Generate signed layout [Alice]")
    create_layout_cmd = "in-toto-layout-gen --signer ../private_keys/alice new_project_layout.toml"
    print(create_layout_cmd)
    subprocess.call(shlex.split(create_layout_cmd))

    prompt_key("Create project (Pull existing project) [Alice]")

    prompt_key("Build project [Alice]")

    prompt_key("Upload wheel and in-toto metadata to RSTUF [Alice]")

    prompt_key("Download and verify wheel [Client]")

    prompt_key("Setup layout to make changes [Alice]")

    prompt_key("Pull project [Bob]")

    prompt_key("Make changes [Bob]")
    
    prompt_key("Build and upload wheel and metadata [Alice]")

    prompt_key("Download and verify updated wheel [Client]")

    print("Adversary does not have Alice's private key")
    prompt_key("Tamper with source code [Adversary]")

    prompt_key("Build and upload new wheel and update RSTUF [Adversary]")

    prompt_key("Download and verify compromised wheel [Client]")


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
