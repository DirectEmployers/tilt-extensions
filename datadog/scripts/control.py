import asyncio
import os
import time
from asyncio import Task

from kubernetes import (
    kubectl_create_secret_from_env_file,
    kubectl_get,
    kubectl_wait,
    kubectl_watch,
)
from tilt import TiltUIButton, TiltUIResource, tilt_get
from variables import (
    BUTTON_DISABLED_PATCH,
    BUTTON_ENABLED_PATCH,
    DISABLE_SIGNAL,
    DISABLED_STATE,
    ENABLE_SIGNAL,
    ENABLED_STATE,
    K8S_CONFIGMAP_SESSIONS,
    K8S_DEPLOYMENT_DATADOG,
    SESSION_PORT,
    TILT_UIRESOURCE_DATADOG_OPERATOR,
)


def serve():
    optr = ExtensionOperator()
    asyncio.run(optr.run())


def remote(keyfile_path: str):
    optr_ui = get_or_create_datadog_operator()
    handle_config_changes(keyfile_path)

    if not optr_ui.is_enabled:
        optr_ui.enable(wait=True)


def handle_config_changes(keyfile_path):
    datadog_api_key = os.getenv("DATADOG_API_KEY", "")
    datadog_app_key = os.getenv("DATADOG_APP_KEY", "")

    if datadog_api_key or datadog_app_key:
        with open(keyfile_path, "w") as f:
            f.write(f"api-key={datadog_api_key}\n")
            f.write(f"app-key={datadog_app_key}\n")

    kubectl_create_secret_from_env_file("datadog-keys", from_env_file=keyfile_path)


def get_session_ports():
    cm = kubectl_get(K8S_CONFIGMAP_SESSIONS)
    sessions = cm.get("data", {})
    return list(sessions.keys())


def get_or_create_datadog_operator():
    kwargs = {"toggle_args": {"resources": "datadog-operator"}}

    for session_port in get_session_ports():
        if tilt_get(TILT_UIRESOURCE_DATADOG_OPERATOR, port=session_port):
            return TiltUIResource("datadog-operator", port=session_port, **kwargs)
    return TiltUIResource("datadog-operator", port=SESSION_PORT, **kwargs)


class SessionController:
    """Handle the state of a Tilt extension in a single Tilt session."""
    port: int
    enabled: bool
    recent_events: dict = {}
    task: Task

    operator: TiltUIResource
    workload: TiltUIResource
    button: TiltUIButton

    def __init__(self, port: int, enable: bool = False):
        self.port = port
        self.enabled = enable

        self.operator = get_or_create_datadog_operator()
        self.workload = TiltUIResource(
            "datadog-agent",
            port=self.port,
            toggle_args={"labels": "datadog"},
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


class ExtensionOperator:
    """Handle a collection of DatadogController instances to manage shared resources."""
    operator_ui: TiltUIResource
    sessions: list[SessionController] = []
    state: str

    def __init__(self):
        self.operator_ui = get_or_create_datadog_operator()
        self.state = ENABLED_STATE if self.is_enabled else DISABLED_STATE

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
        self.state = ENABLED_STATE
        for controller in self.sessions:
            controller.enable()

    def disable(self):
        self.state = DISABLED_STATE
        for controller in self.sessions:
            controller.disable()

    def toggle(self):
        if self.is_enabled:
            self.disable()
        else:
            self.enable()

    def persist_state(self):
        if self.is_enabled:
            self.state = ENABLED_STATE
        else:
            self.state = DISABLED_STATE

    def propogate_state(self):
        if self.state == ENABLED_STATE:
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
