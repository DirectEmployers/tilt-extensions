import json
import os
import signal
from pathlib import Path
from subprocess import run

from moto.moto_api import recorder
from moto.server import ThreadedMotoServer

PORT = os.environ.get("MOTO_PORT", "5000")
IP_ADDRESS = os.environ.get("MOTO_SERVER_IP", "0.0.0.0")
STATE_FILE = Path(os.environ.get("MOTO_RECORDER_FILEPATH"))


def signal_handler(signal, frame):
    """Handle SIGINT and SIGTERM signals."""
    recorder.stop_recording()
    exit(0)


try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except ValueError:
    pass  # ignore "ValueError: signal only works in main thread"


def compact_state():
    """Compact the Moto Recorder state file to avoid making unnecessary requests."""
    compacted = []

    try:
        state = recorder.download_recording()
        with STATE_FILE.open("w") as file:
            for line in state.splitlines():
                request = json.loads(line)

                # Skip all read requests; they don't affect state.
                if request.get("method") in ["GET", "HEAD", "OPTIONS"]:
                    continue

                # These headers vary too much without affecting the actual requests,
                # we remove them to improve the consistency during deduplication.
                varying_headers = ["Authorization", "X-Amz-Date"]

                comparable_headers = {
                    k: v
                    for k, v in request["headers"].items()
                    if k not in varying_headers
                }
                simple_request = dict(request, headers=comparable_headers)

                # Write original JSON line back, with linebreak.
                if simple_request not in compacted:
                    file.write(f"{line}\n")
                    compacted.append(simple_request)
    except FileNotFoundError:
        print("No state file found. Skipping state restoration.")


def restore_state(
    ip_address: str = "0.0.0.0", port: str = "5000", scheme: str = "http"
):
    """Restore state from Moto Recorder state file."""
    try:
        # Restore state from file.
        print("Restoring MotoServer state...")
        recorder.replay_recording(f"{scheme}://{ip_address}:{port}")
    except FileNotFoundError:
        print("No state file found. Skipping state restoration.")


def run_init_script():
    print("Initializing resources...")
    run(["sh", "/motoserver/init.sh"])


if __name__ == "__main__":
    # Start server
    server = ThreadedMotoServer(IP_ADDRESS, PORT)
    server.start()
    recorder_enabled = os.environ.get("MOTO_ENABLE_RECORDING", "true").lower() == "true"

    # Restore prior state from state file if state and recording is not disabled..
    if recorder_enabled:
        compact_state()
        restore_state(IP_ADDRESS, PORT)
    # Keep server alive and prevent script from ending!
    print("MotosServer is ready!")
    # Start recording requests for state
    if recorder_enabled:
        recorder.start_recording()

    # Initialize resources
    run_init_script()
    (Path.home() / "is_ready").touch()
    server._thread.join()
