#!/bin/python3

import os
import sys
import shlex
import subprocess
import argparse
from shutil import copyfile, move, rmtree

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
    show_new_project_layout_cmd = "less new_project_layout.toml"
    print(show_new_project_layout_cmd)
    subprocess.call(shlex.split(show_new_project_layout_cmd))

    prompt_key("Generate and upload signed layout [Alice]")
    generate_new_layout_cmd = (
        "in-toto-layout-gen --signer ../private_keys/alice "
        "new_project_layout.toml")
    print(generate_new_layout_cmd)
    subprocess.call(shlex.split(generate_new_layout_cmd))
    move("root.layout", "../dist")
    os.chdir("../dist")
    upload_layout_cmd = (
        "../rstuf-in-toto-client.py upload-layout root.layout alice.pub")
    print(upload_layout_cmd)
    subprocess.call(shlex.split(upload_layout_cmd))

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
    move("test_project-0.0.1-py3-none-any.whl", "../dist")

    prompt_key("Upload wheel and in-toto metadata to RSTUF [Alice]")
    os.chdir("../dist")
    upload_to_rstuf_cmd = (
        "../rstuf-in-toto-client.py upload-file "
        "test_project-0.0.1-py3-none-any.whl root.layout "
        "build.556caebd.link create.556caebd.link")
    print(upload_to_rstuf_cmd)
    subprocess.call(shlex.split(upload_to_rstuf_cmd))

    prompt_key("Download and verify wheel [Client]")
    os.chdir("../client")
    special_client_download_cmd = ("../rstuf-in-toto-client.py download "
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
    rmtree("dist")
    rmtree("client")
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

    prompt_key("Generate and upload new layout to make changes [Alice]")
    os.chdir("layouts")
    show_change_project_layout_cmd = "less change_project_layout.toml"
    print(show_change_project_layout_cmd)
    subprocess.call(shlex.split(show_change_project_layout_cmd))
    generate_change_layout_cmd = (
        "in-toto-layout-gen --signer ../private_keys/alice "
        "change_project_layout.toml")
    print(generate_change_layout_cmd)
    subprocess.call(shlex.split(generate_change_layout_cmd))
    move("root.layout", "../dist")
    os.chdir("../dist")
    print(upload_layout_cmd)
    subprocess.call(shlex.split(upload_layout_cmd))

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
    move("update.776a00e2.link", "../dist")

    prompt_key("Build and upload wheel and metadata [Alice]")
    build_project_alice_in_toto_run_cmd = (
        "in-toto-run --verbose --step-name build "
        "--key ../private_keys/alice -m pyproject.toml README.md src "
        "-p test_project-0.0.2-py3-none-any.whl --metadata-directory ../dist "
        "-- python3 -m build --wheel --outdir .")
    print(build_project_alice_in_toto_run_cmd)
    subprocess.call(shlex.split(build_project_alice_in_toto_run_cmd))
    move("test_project-0.0.2-py3-none-any.whl", "../dist")
    os.chdir("../dist")
    upload_to_rstuf_cmd = (
        "../rstuf-in-toto-client.py upload-file "
        "test_project-0.0.2-py3-none-any.whl root.layout "
        "clone.776a00e2.link update.776a00e2.link build.556caebd.link")
    print(upload_to_rstuf_cmd)
    subprocess.call(shlex.split(upload_to_rstuf_cmd))

    prompt_key("Download and verify updated wheel [Client]")
    os.chdir("../client")
    special_client_download_cmd = ("../rstuf-in-toto-client.py download "
                                   "test_project-0.0.2-py3-none-any.whl")
    print(special_client_download_cmd)
    subprocess.call(shlex.split(special_client_download_cmd))

    prompt_key("Run test project script [Client]")
    pip_install_cmd = "pip install test_project-0.0.2-py3-none-any.whl"
    print(pip_install_cmd)
    subprocess.call(shlex.split(pip_install_cmd))
    print("run hello-world")
    subprocess.call(shlex.split("hello-world"))

    # ====================================================================
    # Compromise project
    # ====================================================================

    prompt_key("Tamper with source code [Adversary]\n"
               "Adversary does not have Alice's private key")
    os.chdir("../test-project")
    copyfile("../project_files/main.py.compromised", "src/main.py")

    prompt_key("Build and upload new wheel and update RSTUF [Adversary]")
    build_project_adversary_cmd = "python3 -m build --wheel --outdir ."
    print(build_project_adversary_cmd)
    subprocess.call(shlex.split(build_project_adversary_cmd))
    os.remove(os.path.join("../dist", "test_project-0.0.2-py3-none-any.whl"))
    move("test_project-0.0.2-py3-none-any.whl", "../dist")
    os.chdir("../dist")
    upload_to_rstuf_cmd = (
        "../rstuf-in-toto-client.py upload-file "
        "test_project-0.0.2-py3-none-any.whl root.layout "
        "clone.776a00e2.link update.776a00e2.link build.556caebd.link")
    print(upload_to_rstuf_cmd)
    subprocess.call(shlex.split(upload_to_rstuf_cmd))

    prompt_key("Download and verify compromised wheel [Client]")
    os.chdir("..")
    rmtree("client")
    if not os.path.exists("client"):
        os.mkdir("client")
    os.chdir("client")
    special_client_download_cmd = ("../rstuf-in-toto-client.py download "
                                   "test_project-0.0.2-py3-none-any.whl")
    print(special_client_download_cmd)
    subprocess.call(shlex.split(special_client_download_cmd))

    prompt_key("Adversarial changes in wheel successfully caught\n"
               "Force download compromised wheel and run it")
    client_force_download_cmd = (
        "../rstuf-in-toto-client.py download --skip-in-toto-verify "
        "test_project-0.0.2-py3-none-any.whl")
    print(client_force_download_cmd)
    subprocess.call(shlex.split(client_force_download_cmd))
    pip_install_cmd = ("pip install --force-reinstall "
                       "test_project-0.0.2-py3-none-any.whl")
    print(pip_install_cmd)
    subprocess.call(shlex.split(pip_install_cmd))
    print("run hello-world")
    subprocess.call(shlex.split("hello-world"))

    prompt_key("Demo cleanup")
    os.chdir("..")
    clean()


def clean():
    copyfile("project_files/pyproject.toml.original",
             "test-project/pyproject.toml")
    copyfile("project_files/main.py.original", "test-project/src/main.py")
    if os.path.exists("dist"):
        rmtree("dist")
    if os.path.exists("client"):
        rmtree("client")
    subprocess.call(
        shlex.split(
            "./rstuf-in-toto-client.py delete root.layout alice.pub "
            "create.556caebd.link build.556caebd.link clone.776a00e2.link "
            "update.776a00e2.link test_project-0.0.1-py3-none-any.whl "
            "test_project-0.0.2-py3-none-any.whl"))


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

    if args.clean:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        clean()
        sys.exit(0)

    if args.no_prompt:
        global NO_PROMPT
        NO_PROMPT = True

    supply_chain()


if __name__ == '__main__':
    main()
