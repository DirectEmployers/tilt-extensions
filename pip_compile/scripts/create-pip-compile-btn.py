import argparse
import json
import os
from pathlib import Path
from subprocess import run


SCRIPTS = Path.cwd()
DEFAULT_ARGS = "--allow-unsafe --generate-hashes"


def add_pip_compile_buttons(image: str):
    # Get arguments from environment
    env_suffix = image.upper().replace("-", "_")
    target = os.environ[f"PIP_COMPILE_TARGET_{env_suffix}"]
    reqs_path = os.environ[f"PIP_COMPILE_REQSPATH_{env_suffix}"]
    compile_args = os.getenv(f"PIP_COMPILE_ARGS_{env_suffix}", DEFAULT_ARGS)

    # Get DockerImage resources from Tilt:
    # These are used to grab all Tilt uiresources which use `image` and also
    # copies the `docker_build` arguments for the image.
    docker_images_json = run(
        ["tilt", "get", "dockerimages", "-o", "json"],
        capture_output=True,
        text=True,
    )
    images = json.loads(docker_images_json.stdout).get("items", [])

    print(f"Creating pip-compile buttons for {image}:")
    for dockerimage in images:
        # Tilt uiresource and Docker image ref can be split from DockerImage name.
        resource, image_ref = dockerimage["metadata"]["name"].split(":", 1)

        if image_ref != image:
            continue

        print(f"Creating pip-compile button for {resource}...")
        spec = dockerimage.get("spec", {})
        cmd_args = [
            str(SCRIPTS / "pip-compile-container.sh"),
            image_ref,
            spec.get("context", "."),
            spec.get("dockerfile", "Dockerfile"),
            target or spec.get("target", ""),
            reqs_path,
            compile_args,
        ]

        json_config = generate_tilt_json(resource, spec["context"], cmd_args)

        if tilt_apply(json_config).returncode == 0:
            print(f"- Created pip-compile button for {resource}")
        else:
            print(f"- Could not create pip-compile button for {resource}")


def tilt_apply(json_config):
    return run(["tilt", "apply", "-f", "-"], input=json_config.encode("utf-8"))


def tilt_resource_template(kind: str) -> dict:
    return {
        "apiVersion": "tilt.dev/v1alpha1",
        "kind": kind,
        "metadata": {},
        "spec": {},
    }


def generate_tilt_json(resource: str, context: str, arguments: list[str]):
    btn_name = f"{resource}:btn:pip-compile"
    log_span_id = f"{resource}:pip-compile"

    uibutton = tilt_resource_template("UIButton")
    uibutton["metadata"]["name"] = btn_name
    uibutton["spec"] = {
        "location": {
            "componentType": "Resource",
            "componentID": resource,
        },
        "iconName": "build_circle",
        "text": "pip-compile",
    }

    cmd = tilt_resource_template("Cmd")
    cmd["metadata"] = {
        "name": f"{resource}:pip-compile",
        "annotations": {
            "tilt.dev/resource": resource,
            "tilt.dev/log-span-id": log_span_id,
        },
    }
    cmd["spec"] = {
        "args": arguments,
        "dir": context,
        "startOn": {"uiButtons": [btn_name]},
    }

    resources = {
        "apiVersion": "tilt.dev/v1alpha1",
        "kind": "List",
        "items": [uibutton, cmd],
    }

    return json.dumps(resources)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("pip-compile-button")
    parser.add_argument("image", type=str)
    args = parser.parse_args()

    # Create pip-compile buttons on resources using image
    add_pip_compile_buttons(args.image)
