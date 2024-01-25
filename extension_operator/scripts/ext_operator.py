import asyncio

from kubernetes import kubectl_get, kubectl_watch

from constants import (
    DISABLE_SIGNAL,
    DISABLED,
    ENABLE_SIGNAL,
    ENABLED,
    K8S_CONFIGMAP_SESSIONS,
    K8S_DEPLOYMENT_DATADOG,
)
from session_controller import SessionController
from tilt.api_resources import TiltUIResource
from tilt.utils import get_or_create_extension_operator


class ExtensionOperator:
    """Handle a collection of DatadogController instances to manage shared resources."""
    operator_ui: TiltUIResource
    sessions: list[SessionController] = []
    state: str

    def __init__(self):
        self.operator_ui = get_or_create_extension_operator()
        self.state = ENABLED if self.is_enabled else DISABLED

    def get_session(self, port: int) -> SessionController | None:
        for controller in self.sessions:
            if port == controller.port:
                return controller
        return None

    def get_operator(self) -> SessionController | None:
        for controller in self.sessions:
            if controller.operator.exists():
                return controller
        return None

    @property
    def is_running(self) -> bool:
        return bool(self.get_operator())

    @property
    def is_enabled(self) -> bool:
        k8s_resource = kubectl_get(K8S_DEPLOYMENT_DATADOG)
        return bool(k8s_resource)

    def enable(self):
        self.state = ENABLED
        for controller in self.sessions:
            controller.enable()

    def disable(self):
        self.state = DISABLED
        for controller in self.sessions:
            controller.disable()

    def toggle(self):
        if self.is_enabled:
            self.disable()
        else:
            self.enable()

    def persist_state(self):
        if self.is_enabled:
            self.state = ENABLED
        else:
            self.state = DISABLED

    def propogate_state(self):
        if self.state == ENABLED:
            self.enable()
        else:
            self.disable()

    async def watch(self, session: SessionController):
        """Watch for new events from controller and pass to event_handler."""
        async for event in session.run():
            print(f"{event} signal received")
            if event == ENABLE_SIGNAL:
                self.enable()
            if event == DISABLE_SIGNAL:
                self.disable()

    async def run(self):
        """Watch for relevant changes, update controller directives.

        Handle creation/destruction of Tilt sessions
        """
        async with asyncio.TaskGroup() as tg:
            async for new_sessions in kubectl_watch(K8S_CONFIGMAP_SESSIONS, "data"):
                # Terminate inactive sessions
                for i, old_session in enumerate(self.sessions):
                    # Delete SessionController and cancel its task
                    if old_session.port not in new_sessions:
                        self.sessions.pop(i)

                # Handle new and existing sessions
                for new_port in new_sessions.keys():
                    # Ignore existing sessions
                    if self.get_session(new_port):
                        continue

                    # Create new session and wrap it in a task to watch it
                    session = SessionController(new_port, self.is_enabled)
                    session.attach_task(
                        tg.create_task(self.watch(session)),
                    )
                    self.sessions.append(session)
