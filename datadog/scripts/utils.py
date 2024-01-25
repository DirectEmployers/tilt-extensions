import asyncio
import json
import subprocess


def run(command: list[str], output_type: str = "default"):
    proc = subprocess.run(command, stdout=subprocess.PIPE)

    success = proc.stdout and not proc.returncode
    if success and output_type == "json":
        return json.loads(proc.stdout)

    if not success:
        print("Error:", proc.stderr)

    return proc.stdout


async def async_run(args):
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
    )

    while (data := await proc.stdout.readline()) is not None:
        if line := data.decode("utf-8").strip():
            yield line

    await proc.wait()
