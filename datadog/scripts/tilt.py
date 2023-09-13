from pathlib import Path

from utils import async_run, run
from variables import TILT_UIBUTTON_TOGGLE_DATADOG_AGENT


async def tilt_watch(resource: str, jsonpath: str, port: int | None = None):
    args = [
        "tilt",
        "get",
        resource,
        f'-o=jsonpath={{$.{jsonpath}}}{{"\\n"}}',
        "--watch",
    ]

    if port:
        args.extend(["--port", port])

    async for line in async_run(args):
        yield line


def tilt_get(
    resource: str,
    port: int | None = None,
    output_type: str = "json",
    watch: bool = False,
):
    args = ["tilt", "get", resource, "--output", output_type]

    if port:
        args.extend(["--port", port])

    if watch:
        args.extend(["--watch"])

    return run(args, output_type)


def tilt_disable(
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    args = ["tilt", "disable"]

    if isinstance(resources, str):
        args.append(resources)
    elif isinstance(resources, list):
        args.extend(resources)

    if labels is not None:
        args.append("--labels")
        if isinstance(labels, str):
            args.append(labels)
        elif isinstance(labels, list):
            args.extend(labels)

    if port:
        args.extend(["--port", port])

    return run(args)


def tilt_enable(
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    args = ["tilt", "enable"]

    if isinstance(resources, str):
        args.append(resources)
    elif isinstance(resources, list):
        args.extend(resources)

    if labels is not None:
        args.append("--labels")
        if isinstance(labels, str):
            args.append(labels)
        elif isinstance(labels, list):
            args.extend(labels)

    if port:
        args.extend(["--port", port])

    return run(args)


def tilt_patch(resource: str, config: str, port: int | None = None):
    args = ["tilt", "patch", resource, "-p", config]

    if port:
        args.extend(["--port", port])

    return run(args)


def update_button(svg_path: Path):
    with svg_path.open(encoding="utf-8") as file:
        svg = file.read().strip()
        tilt_patch(
            TILT_UIBUTTON_TOGGLE_DATADOG_AGENT,
            f'{{"spec":{{"iconSVG":"{svg}"}}}}',
        )
