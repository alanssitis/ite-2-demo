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
    upload_to_rstuf_cmd = (
            "../rstuf-in-toto-client.py upload "
            "test_project-0.0.1-py3-none-any.whl root.layout alice.pub "
            "build.556caebd.link create.556caebd.link")
    print(upload_to_rstuf_cmd)
    subprocess.call(shlex.split(upload_to_rstuf_cmd))

    prompt_key("Download and verify wheel [Client]")
    os.chdir("../client")
    special_client_download_cmd = (
            "../rstuf-in-toto-client.py download "
            "test_project-0.0.1-py3-none-any.whl")
    print(special_client_download_cmd)
    subprocess.call(shlex.split(special_client_download_cmd))

    prompt_key("Run test project script [Client]")
    pip_install_cmd = "pip install test_project-0.0.1-py3-none-any.whl"
    print(pip_install_cmd)
    subprocess.call(shlex.split(pip_install_cmd))
    subprocess.call(shlex.split("hello-world"))

    prompt_key("Clear /dist and /client and RSTUF bins")
    os.chdir("..")
    clear_dist_cmd = "rm -rf dist"
    print(clear_dist_cmd)
    subprocess.call(shlex.split(clear_dist_cmd))
    clear_client_cmd = "rm -rf client"
    print(clear_client_cmd)
    subprocess.call(shlex.split(clear_client_cmd))
    delete_rstuf_cmd = (
            "./rstuf-in-toto-client.py delete root.layout alice.pub "
            "create.556caebd.link build.556caebd.link "
            "test_project-0.0.1-py3-none-any.whl")
    print(delete_rstuf_cmd)
    subprocess.call(shlex.split(delete_rstuf_cmd))

    if not os.path.exists("dist"):
        os.mkdir("dist")
    if not os.path.exists("client"):
        os.mkdir("client")
    copyfile("layouts/keys/alice.pub", "dist/alice.pub")

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
    upload_to_rstuf_cmd = (
            "../rstuf-in-toto-client.py upload "
            "test_project-0.0.2-py3-none-any.whl root.layout alice.pub "
            "clone.776a00e2.link update.776a00e2.link build.556caebd.link")
    print(upload_to_rstuf_cmd)
    subprocess.call(shlex.split(upload_to_rstuf_cmd))

    prompt_key("Download and verify updated wheel [Client]")
    os.chdir("../client")
    special_client_download_cmd = (
            "../rstuf-in-toto-client.py download "
            "test_project-0.0.2-py3-none-any.whl")
    print(special_client_download_cmd)
    subprocess.call(shlex.split(special_client_download_cmd))

    prompt_key("Run test project script [Client]")
    pip_install_cmd = "pip install test_project-0.0.2-py3-none-any.whl"
    print(pip_install_cmd)
    subprocess.call(shlex.split(pip_install_cmd))
    subprocess.call(shlex.split("hello-world"))

    # ====================================================================
    # Compromise project
    # ====================================================================

    prompt_key("Tamper with source code [Adversary]\nAdversary does not have Alice's private key")
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
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        copyfile("project_files/pyproject.toml.original",
                 "test-project/pyproject.toml")
        copyfile("project_files/main.py.original", "test-project/src/main.py")
        rmtree("dist")
        rmtree("client")
        sys.exit(0)

    if args.no_prompt:
        global NO_PROMPT
        NO_PROMPT = True

    supply_chain()


if __name__ == '__main__':
    main()
