from asyncio import Task

from tilt.api_resources import TiltAPIResource, TiltUIResource
from tilt.utils import get_or_create_extension_operator


class ExtensionController:
    """Handle the state of a Tilt extension in a single Tilt session."""
    port: int
    enabled: bool
    recent_events: dict = {}
    task: Task

    operator: TiltUIResource
    resources: list[TiltAPIResource]

    def __init__(
        self,
        resources: list[TiltAPIResource],
        port: int,
        enable: bool = False,
    ):
        self.port = port
        self.enabled = enable

        self.operator = get_or_create_extension_operator()
        self.resources = resources

    def __del__(self):
        self.task.cancel()

    def attach_task(self, task: Task):
        self.task = task

    @property
    def is_operator(self):
        return self.port == self.operator.port

    def enable(self):
        for resource in self.resources:
            resource.enable()

    def disable(self):
        for resource in self.resources:
            resource.disable()

    async def run(self):
        """Watch for relevant changes in Tilt, update controllers."""
        for resource in self.resources:
            yield resource.watch()
