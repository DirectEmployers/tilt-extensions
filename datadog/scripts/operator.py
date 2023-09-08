import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Any, NamedTuple

logger = logging.getLogger(__name__)


UIRESOURCE = "datadog-agent"
UIBUTTON = "de-remote:toggle-datadog-agent"


class ControllerEvent(NamedTuple):
    resource: str
    key: str
    value: Any


def cmd(command: list[str], output_type: str = "default"):
    proc = subprocess.run(command, stdout=subprocess.PIPE)

    success = proc.stdout and not proc.returncode
    if output_type == "json":
        return json.loads(proc.stdout) if success else {}

    return proc.stdout if success else ""


async def cmdline_generator(args):
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
    )

    while line := await proc.stdout.readline():
        if line := line.decode("utf-8").strip():
            yield line

    await proc.wait()


def tilt_watch(resource: str, jsonpath: str, port: int | None = None):
    args = [
        "tilt",
        "get",
        resource,
        f'-o=jsonpath=\'{{$.{jsonpath}}}{{"\\n"}}\'',
        "--watch-only",
    ]

    if port:
        args.extend(["--port", port])

    return cmdline_generator(args)


def kubectl_get(
    resource: str,
    name: str | None = None,
    output_type: str = "json",
    watch: bool = False,
):
    if name:
        resource += f"/{name}"

    args = ["kubectl", "get", resource, "--output", output_type]

    if watch:
        args.extend(["--watch"])

    return cmd(args, output_type)


def tilt_get(
    resource: str,
    name: str | None = None,
    port: int | None = None,
    output_type: str = "json",
    watch: bool = False,
):
    if name:
        resource += f"/{name}"

    args = ["tilt", "get", resource, "--output", output_type]

    if port:
        args.extend(["--port", port])

    if watch:
        args.extend(["--watch"])

    return cmd(args, output_type)


class DatadogController:
    """Handle the state of a Tilt extension in a single Tilt session."""
    tilt_port: int
    state: dict = {}

    def __init__(self, port: int):
        self.tilt_port = port

    @property
    def is_controller(self):
        return self.tilt_port == os.environ["TILT_PORT"]

    @property
    def has_uiresource(self) -> bool:
        return bool(tilt_get("uiresource", UIRESOURCE, port=self.tilt_port))

    @property
    def has_uibutton(self) -> bool:
        return bool(tilt_get("uibutton", UIBUTTON, port=self.tilt_port))

    def enable(self):
        cmd(["tilt", "enable", "datadog-operator", "--labels", "datadog", "--port", self.tilt_port])

    def disable(self):
        cmd(["tilt", "disable", "--labels", "datadog", "--port", self.tilt_port])

    def has_changed(self, event: ControllerEvent):
        return self.state.get(f"{event.resource}:{event.key}") != event.value

    def update_state(self, event: ControllerEvent):
        self.state[f"{event.resource}:{event.key}"] = event.value

    async def handle(self):
        """Watch for relevant changes in Tilt, update controllers."""

        # Watch for UIButton usage
        event_type = "status.lastClickedAt"
        uibutton_status = tilt_watch(
            f"uibutton/{UIBUTTON}",
            event_type,
            port=self.tilt_port
        )

        async for value in uibutton_status:
            event = ControllerEvent(UIBUTTON, event_type, value)
            if self.has_changed(event):
                self.update_state(event)
                # Send click event to Operator
                yield event

        # Watch for UIResource state changes
        event_type = "status.disableStatus.state"
        uiresource_status = tilt_watch(
            f"uibutton/{UIRESOURCE}",
            "status.disableStatus.state",
            port=self.tilt_port
        )

        async for value in uiresource_status:
            event = ControllerEvent(UIRESOURCE, event_type, value)
            if self.has_changed(event):
                self.update_state(event)
                # Send state event to Operator
                yield event


class DatadogOperator:
    """Handle a collection of DatadogController instances to manage shared resources."""
    controllers: list[DatadogController] = []

    def __init__(self):
        self.init_controllers()

    @property
    def is_enabled(self) -> bool:
        k8s_resource = kubectl_get("deployment", "datadog-agent")
        return bool(k8s_resource)

    @property
    def active_sessions(self):
        cm = kubectl_get("configmap", "tilt-active-sessions")
        sessions = cm.get("data", {})
        return list(sessions.keys())

    def init_controllers(self):
        for port in self.active_sessions:
            self.controllers.append(DatadogController(port))

    def enable(self):
        for controller in self.controllers:
            controller.enable()

    def disable(self):
        for controller in self.controllers:
            controller.disable()

    async def handle(self):
        """Watch for relevant changes, update controller directives."""
        # TODO: Handle creation/destruction of controllers/sessions!!!
        for controller in self.controllers:
            async for event in controller.handle():
                # Handle UIButton events
                if event.resource == UIBUTTON:
                    # Propagate correct state to controllers
                    if self.is_enabled:
                        self.disable()
                    else:
                        self.enable()

                # Handle UIResource events
                if event.resource == UIRESOURCE:
                    # Propagate correct state to controllers
                    if event.key == "Enabled" and not self.is_enabled:
                        self.enable()
                    elif event.key == "Disabled" and self.is_enabled:
                        self.disable()


if __name__ == "__main__":
    operator = DatadogOperator()
    asyncio.run(operator.handle())
    while True:
        time.sleep(120)
