import json

from utils import async_run, run


async def tilt_watch(
    resource: str,
    jsonpath: str | None = None,
    output: str = "jsonpath",
    watch: bool = True,
    watch_only: bool = False,
    port: int | None = None,
):
    args = [
        "tilt",
        "get",
        resource,
    ]

    if output == "jsonpath" and jsonpath:
        args.append(f'-o=jsonpath={{$.{jsonpath}}}{{"\\n"}}')
    else:
        args.extend(["--output", output])

    if watch_only:
        args.append("--watch-only")
    elif watch:
        args.append("--watch")

    if port:
        args.extend(["--port", port])

    buffer = ""
    async for line in async_run(args):
        if output == "json":
            try:
                yield json.loads(buffer + line)
                buffer = ""
            except json.decoder.JSONDecodeError:
                buffer += line
                continue
        else:
            yield line


def tilt_wait(
    resource: str,
    wait_for: str,
    timeout: str = "30s",
    output_type: str = "json",
    port: int | None = None,
):
    args = [
        "tilt",
        "wait",
        resource,
        f"--for={wait_for}",
        f"--timeout={timeout}",
        f"--output={output_type}",
    ]

    if port:
        args.extend(["--port", port])

    return run(args, output_type)


def tilt_get(
    resource: str,
    watch: bool = False,
    output_type: str = "json",
    port: int | None = None,
):
    args = ["tilt", "get", resource, "--output", output_type]

    if port:
        args.extend(["--port", port])

    if watch:
        args.extend(["--watch"])

    return run(args, output_type)


def _tilt_enable(
    enable: bool = True,
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    op = "enable" if enable else "disable"
    args = ["tilt", op]

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
    return _tilt_enable(
        enable=True,
        resources=resources,
        labels=labels,
        port=port,
    )


def tilt_disable(
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    return _tilt_enable(
        enable=False,
        resources=resources,
        labels=labels,
        port=port,
    )


def tilt_trigger(resource: str, port: int | None = None):
    args = ["tilt", "trigger", resource]

    if port:
        args.extend(["--port", port])

    return run(args)


def tilt_patch(
    resource: str,
    config: str,
    patch_type: str = "strategic",
    port: int | None = None,
):
    args = ["tilt", "patch", resource, "--type", patch_type, "-p", config]

    if port:
        args.extend(["--port", port])

    return run(args)
