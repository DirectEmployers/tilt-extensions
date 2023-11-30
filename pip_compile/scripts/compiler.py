import argparse
import json
import subprocess
import tempfile
from pathlib import Path

BUILD_TAG = "build"

SCRIPTS = Path(__file__).parent

# Container Paths
CONTAINER_REQUIREMENTS_PATH = "/.pip-requirements/mount/"
CONTAINER_SCRIPTS_PATH = "/.pip-requirements/scripts/"


def build_image(image, tilt_resource, target):
    dockerimages_json = subprocess.run(
        ["tilt", "get", "dockerimages", f"{tilt_resource}:{image}", "-o", "json"],
        capture_output=True,
        text=True,
    )
    dockerimages = json.loads(dockerimages_json.stdout)
    spec = dockerimages["spec"]

    # with tempfile.NamedTemporaryFile(mode="w+") as dockerfile:
    #     # Create temporary Dockerfile.
    #     dockerfile.write(spec["dockerfileContents"])
    #     dockerfile.close()
    #
    #     print(dockerfile.name)

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
    process = subprocess.run(
        docker_build,
        input=spec["dockerfileContents"].encode("utf-8"),
    )

    if process.returncode != 0:
        print("Error: Docker image failed to build")
        print(process.stdout, process.stderr)
        exit(1)


def run_container(image, compile_args, local_req_path):
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
    process = subprocess.run(docker_run)
    if process.returncode != 0:
        print("Error: Pip requirements failed to compile")
        exit(2)


def compile_requirements(
    image: str,
    resource: str,
    target: str,
    local_req_path: Path,
    compile_args: list[str],
):
    """Build and run image to build pip requirements with pip-tools."""
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
