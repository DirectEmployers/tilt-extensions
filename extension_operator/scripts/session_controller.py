import time
from asyncio import Task

from constants import (
    BUTTON_DISABLED_PATCH,
    BUTTON_ENABLED_PATCH,
    K8S_DEPLOYMENT_DATADOG,
)
from extension_controller import ExtensionController
from k8s.command import kubectl_wait
from tilt.api_resources import TiltUIButton, TiltUIResource
from tilt.utils import get_or_create_extension_operator


class SessionController:
    """Handle the state of a Tilt extension in a single Tilt session."""
    port: int
    enabled: bool
    recent_events: dict = {}
    task: Task

    operator: TiltUIResource
    extensions: list [ExtensionController]

    def __init__(self, port: int, enable: bool = False):
        self.port = port
        self.enabled = enable

        self.operator = get_or_create_extension_operator()
        self.workload = TiltUIResource(
            "datadog-agent",
            toggle_args={"labels": "datadog"},
            port=self.port,
        )
        self.button = TiltUIButton(
            "de-remote:toggle-datadog-agent",
            patch_enable=BUTTON_ENABLED_PATCH,
            patch_disable=BUTTON_DISABLED_PATCH,
            port=self.port,
        )

    def __del__(self):
        self.task.cancel()

    def attach_task(self, task: Task):
        self.task = task

    @property
    def is_operator(self):
        return self.port == self.operator.port

    def enable(self):
        self.button.enable()

        if not self.is_operator:
            time.sleep(5)
            print("Waiting for Datadog deployment to start...")
            kubectl_wait(K8S_DEPLOYMENT_DATADOG, "condition=available", timeout="120s")
        self.workload.enable()

    def disable(self):
        self.button.disable()
        self.workload.disable()

    async def run(self):
        """Watch for relevant changes in Tilt, update controllers."""
        async for e in self.button.watch():
            yield e
        async for e in self.workload.watch():
            yield e
