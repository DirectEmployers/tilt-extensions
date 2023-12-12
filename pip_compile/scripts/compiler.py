import argparse
import json
import subprocess
from pathlib import Path

BUILD_TAG = "build"

SCRIPTS = Path(__file__).parent

# Container Paths
CONTAINER_REQUIREMENTS_PATH = "/.pip-requirements/mount/"
CONTAINER_SCRIPTS_PATH = "/.pip-requirements/scripts/"


def build_image(image: str, tilt_resource: str, target: str):
    """Build the container image which will be used run `pip-compile`.

    :param image:
    :param tilt_resource:
    :param target:
    :return:
    """
    dockerimages_json = subprocess.run(
        ["tilt", "get", "dockerimages", f"{tilt_resource}:{image}", "-o", "json"],
        capture_output=True,
        text=True,
    )
    dockerimages = json.loads(dockerimages_json.stdout)
    spec = dockerimages["spec"]

    docker_build = [
        "docker",
        "build",
        "--quiet",
        f"--tag={image}:{BUILD_TAG}",
        f"--target={target}",
        f"--cache-from={image}",
        "--file=-",
        spec["context"],
    ]

    try:
        subprocess.run(
            docker_build,
            check=True,
            input=spec["dockerfileContents"].encode("utf-8"),
        )
    except subprocess.CalledProcessError:
        print("Error: Docker image failed to build")
        raise


def run_container(image: str, compile_args: list[str], local_req_path: Path):
    """Run a container with the required mounts to compile requirements.

    :param image:
    :param compile_args:
    :param local_req_path:
    :return:
    """
    docker_run = [
        "docker",
        "run",
        "-i",
        "--rm",
        "--user=0",
        f"--name=pip-compile-{image}",
        f"--volume={local_req_path}:{CONTAINER_REQUIREMENTS_PATH}:rw",
        f"--volume={SCRIPTS}:{CONTAINER_SCRIPTS_PATH}:ro",
        f"--entrypoint={CONTAINER_SCRIPTS_PATH}/entrypoint.sh",
        f"{image}:{BUILD_TAG}",
    ]
    docker_run.extend(compile_args)

    try:
        subprocess.run(docker_run, check=True)
    except subprocess.CalledProcessError:
        print("Error: Pip requirements failed to compile")
        raise


def compile_requirements(
    image: str,
    resource: str,
    target: str,
    local_req_path: Path,
    compile_args: list[str],
):
    """Build and run image to build pip requirements with pip-tools.

    :param image:
    :param resource:
    :param target:
    :param local_req_path:
    :param compile_args:
    :return:
    """
    # Prepare the container image to run `pip-compile`.
    build_image(image, resource, target)

    # Compile pip requirements.
    print("Please wait: Compiling pip requirements with pip-tools...")
    run_container(image, compile_args, local_req_path)

    print("Done: pip requirements have been compiled!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("pip-compile-container")
    parser.add_argument("image", type=str)
    parser.add_argument("resource", type=str)
    parser.add_argument("--target", type=str)
    parser.add_argument("--reqs-path", type=Path)
    parser.add_argument("--compile-args", action="append")

    args = parser.parse_args()
    compile_requirements(
        args.image,
        args.resource,
        args.target,
        args.reqs_path,
        args.compile_args,
    )
