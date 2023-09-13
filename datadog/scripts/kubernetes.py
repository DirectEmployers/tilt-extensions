from utils import run


def kubectl_get(resource: str, output_type: str = "json", watch: bool = False,
):
    args = ["kubectl", "get", resource, "--output", output_type]

    if watch:
        args.extend(["--watch"])

    return run(args, output_type)
