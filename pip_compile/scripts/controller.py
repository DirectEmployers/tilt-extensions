import argparse
import json
import subprocess
from pathlib import Path


SCRIPTS = Path(__file__).parent


def get_enabled_tilt_resources() -> list[str]:
    """List the enabled UIResource names from Tilt API."""
    resources_json = subprocess.run(
        ["tilt", "get", "uiresources", "-o", "json"],
        capture_output=True,
        text=True,
    )
    resources = json.loads(resources_json.stdout).get("items", [])
    return [
        r["metadata"]["name"] for r in resources
        if r["status"]["disableStatus"]["state"] == "Enabled"
    ]


def get_tilt_dockerimages() -> list[dict]:
    """List DockerImage objects from Tilt API."""
    docker_images_json = subprocess.run(
        ["tilt", "get", "dockerimages", "-o", "json"],
        capture_output=True,
        text=True,
    )
    return json.loads(docker_images_json.stdout).get("items", [])


def update_image_resources(
    image: str,
    target: str,
    reqs_path: Path,
    compile_args: list[str],
):
    enabled_resources = get_enabled_tilt_resources()
    resource_images = get_tilt_dockerimages()

    print(f"🛠️ Creating pip-compile buttons for Tilt UI resources using {image} image:")
    for dockerimage in resource_images:
        # Tilt uiresource and Docker image ref can be split from DockerImage name.
        resource, image_ref = dockerimage["metadata"]["name"].split(":", 1)

        # Only add buttons to enabled resources using the same image.
        if image_ref == image and resource in enabled_resources:
            spec = dockerimage["spec"]
            cmd_args = get_cmd_args(image, resource, target, reqs_path, compile_args)
            json_config = generate_tilt_json(resource, spec["context"], cmd_args)

            process = tilt_apply(json_config)
            if process.returncode == 0:
                print(f"✅ {resource}… success!")
            else:
                print("❌ {resource}… error!", process.stdout, process.stderr, "")


def get_cmd_args(
    image: str,
    resource: str,
    target: str,
    reqs_path: Path,
    compile_args: list[str],
) -> list[str]:
    cmd_args = [
        "python",
        str(SCRIPTS / "compiler.py"),
        image,
        resource,
        f"--target={target}",
        f"--reqs-path={reqs_path}",
    ]
    for arg in compile_args:
        cmd_args.append("--compile-args=%s" % arg)

    return cmd_args


def tilt_apply(json_config: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["tilt", "apply", "-f", "-"],
        capture_output=True,
        input=json_config,
        text=True,
    )


def tilt_resource_template(kind: str) -> dict:
    return {
        "apiVersion": "tilt.dev/v1alpha1",
        "kind": kind,
        "metadata": {},
        "spec": {},
    }


def generate_tilt_json(resource: str, context: str, arguments: list[str]) -> str:
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


def run_controller(image: str, target: str, reqs_path: Path, compile_args: list[str]):
    """Apply `pip-compile` buttons when relevant Tilt resources change.

    Relevant Tilt UI Resources are those which consume the same Docker image which the
    `pip-compile` extension has been configured for.
    """

    print(
        f"🕵️‍♀️ pip-compile-controller:{image} monitors the state of Tilt resources.\n"
        "ℹ️ The controller will add a 'pip-compile' button to any Tilt UI resource "
        f"which uses the {image} image.\n"
    )

    imagemaps = subprocess.Popen(
        ["tilt", "get", "imagemaps", "--watch-only", "-o", "name"],
        stdout=subprocess.PIPE,
        text=True,
    )

    for imagemap in imagemaps.stdout:
        image_ref = imagemap.strip().split("/")[-1]
        if image_ref == image:
            update_image_resources(image, target, reqs_path, compile_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("pip-compile-controller")
    parser.add_argument("image", type=str)
    parser.add_argument("--target", type=str)
    parser.add_argument("--reqs-path", type=Path)
    parser.add_argument("--compile-args", action="append")

    args = parser.parse_args()
    run_controller(args.image, args.target, args.reqs_path, args.compile_args)
