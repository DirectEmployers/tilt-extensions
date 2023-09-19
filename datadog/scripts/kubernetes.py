import json

from utils import async_run, run


def kubectl_get(resource: str, output_type: str = "json", watch: bool = False):
    args = ["kubectl", "get", resource, "--output", output_type]

    if watch:
        args.extend(["--watch"])

    return run(args, output_type)


def kubectl_wait(
    resource: str,
    wait_for: str,
    timeout: str = "30s",
):
    args = [
        "kubectl",
        "wait",
        resource,
        f"--for={wait_for}",
        f"--timeout={timeout}",
    ]

    return run(args)


async def kubectl_watch(
    resource: str,
    jsonpath: str,
    watch: bool = True,
    watch_only: bool = False,
):
    args = [
        "kubectl",
        "get",
        resource,
        f'-o=jsonpath={{$.{jsonpath}}}{{"\\n"}}',
    ]

    if watch_only:
        args.append("--watch-only")
    elif watch:
        args.append("--watch")

    async for line in async_run(args):
        yield json.loads(line)
