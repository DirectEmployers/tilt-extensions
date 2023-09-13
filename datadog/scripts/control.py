import asyncio

from tilt import tilt_disable, tilt_enable, tilt_get, tilt_watch, update_button

from events import Event, TiltEvents
from kubernetes import kubectl_get
from variables import (
    EXTENSION_STATE_DISABLED, EXTENSION_STATE_ENABLED, K8S_CONFIGMAP_SESSIONS,
    K8S_DEPLOYMENT_DATADOG, SVG_DISABLED, SVG_ENABLED,
    TILT_UIBUTTON_TOGGLE_DATADOG_AGENT, TILT_UIRESOURCE_DATADOG_AGENT,
    TILT_UIRESOURCE_DATADOG_OPERATOR,
)


class SessionController:
    """Handle the state of a Tilt extension in a single Tilt session."""
    port: int
    enabled: bool
    recent_events: dict = {}

    def __init__(self, port: int, enabled: bool = False):
        self.enabled = enabled
        self.port = port

    @property
    def has_operator(self) -> bool:
        return bool(tilt_get(TILT_UIRESOURCE_DATADOG_OPERATOR, port=self.port))

    @property
    def has_uiresource(self) -> bool:
        return bool(tilt_get(TILT_UIRESOURCE_DATADOG_AGENT, port=self.port))

    @property
    def has_uibutton(self) -> bool:
        return bool(tilt_get(TILT_UIBUTTON_TOGGLE_DATADOG_AGENT, port=self.port))

    def enable(self):
        if not self.enabled:
            update_button(SVG_ENABLED)
            tilt_enable("datadog-operator", labels="datadog", port=self.port)
            print(f"Enabled session at port {self.port}")

    def disable(self):
        if self.enabled:
            update_button(SVG_DISABLED)
            tilt_disable(labels="datadog", port=self.port)
            print(f"Enabled session at port {self.port}")

    def _has_changed(self, event: Event):
        return self.recent_events.get(event.alias) != event.value

    def _update_state(self, event: Event):
        self.recent_events[event.alias] = event.value

    async def _watch_event(self, event_alias):
        """Yield changes in event state."""
        event_args = TiltEvents.aliases.get(event_alias)

        if not event_args:
            raise Exception(f"TiltEvent not found for alias: '{event_alias}'")

        async for value in tilt_watch(*event_args, port=self.port):
            event = Event(resource=event_args[0], alias=event_alias, value=value)
            if self._has_changed(event):
                self._update_state(event)
                yield event

    async def handle(self):
        """Watch for relevant changes in Tilt, update controllers."""
        async for e in self._watch_event("datadog:button.click"):
            yield e
        async for e in self._watch_event("datadog:workload.status"):
            yield e


class ExtensionOperator:
    """Handle a collection of DatadogController instances to manage shared resources."""
    controllers: list[SessionController] = []
    state: str

    def __init__(self):
        self.init_controllers()
        self.persist_state()
        self.propogate_state()

    def init_controllers(self):
        for port in self.active_sessions:
            self.controllers.append(SessionController(port))

    def get_operator(self) -> int | None:
        for controller in self.controllers:
            if controller.has_operator:
                return controller.port
        return None

    @property
    def is_running(self) -> bool:
        return bool(self.get_operator())

    @property
    def is_enabled(self) -> bool:
        k8s_resource = kubectl_get(K8S_DEPLOYMENT_DATADOG)
        return bool(k8s_resource)

    @property
    def active_sessions(self):
        cm = kubectl_get(K8S_CONFIGMAP_SESSIONS)
        sessions = cm.get("data", {})
        return list(sessions.keys())

    def enable(self):
        self.state = EXTENSION_STATE_ENABLED
        for controller in self.controllers:
            controller.enable()

    def disable(self):
        self.state = EXTENSION_STATE_DISABLED
        for controller in self.controllers:
            controller.disable()

    def toggle(self):
        if self.is_enabled:
            self.disable()
        else:
            self.enable()

    def persist_state(self):
        if self.is_enabled:
            self.state = EXTENSION_STATE_ENABLED
        else:
            self.state = EXTENSION_STATE_DISABLED

    def propogate_state(self):
        if self.state == EXTENSION_STATE_ENABLED:
            self.enable()
        else:
            self.disable()

    async def handle_controller(self, controller):
        """Watch for new events from controller and pass to event_handler."""
        async for event in controller.handle():
            print(f"Event from port #{controller.port}: {event.alias} {event.value}")
            match event:
                case e if e.alias == "datadog:button.click":
                    self.toggle()
                case e if e.value == EXTENSION_STATE_ENABLED:
                    self.enable()
                case e if e.value == EXTENSION_STATE_DISABLED:
                    self.disable()

    async def run(self):
        """Watch for relevant changes, update controller directives."""

        # TODO: Handle creation/destruction of controllers/sessions!!!
        await asyncio.gather(
            *[
                asyncio.create_task(self.handle_controller(c))
                for c in self.controllers
            ],
        )
