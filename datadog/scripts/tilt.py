import json
from dataclasses import dataclass, field
from datetime import datetime

from utils import async_run, run
from variables import DISABLE_SIGNAL, ENABLE_SIGNAL, ENABLED_STATE


async def tilt_watch(
    resource: str,
    jsonpath: str | None = None,
    output: str = "jsonpath",
    watch: bool = True,
    watch_only: bool = False,
    port: int | None = None,
):
    args = [
        "tilt",
        "get",
        resource,
    ]

    if output == "jsonpath" and jsonpath:
        args.append(f'-o=jsonpath={{$.{jsonpath}}}{{"\\n"}}')
    else:
        args.extend(["--output", output])

    if watch_only:
        args.append("--watch-only")
    elif watch:
        args.append("--watch")

    if port:
        args.extend(["--port", port])

    buffer = ""
    async for line in async_run(args):
        if output == "json":
            try:
                yield json.loads(buffer + line)
                buffer = ""
            except json.decoder.JSONDecodeError:
                buffer += line
                continue
        else:
            yield line


def tilt_wait(
    resource: str,
    wait_for: str,
    timeout: str = "30s",
    output_type: str = "json",
    port: int | None = None,
):
    args = [
        "tilt",
        "wait",
        resource,
        f"--for={wait_for}",
        f"--timeout={timeout}",
        f"--output={output_type}",
    ]

    if port:
        args.extend(["--port", port])

    return run(args, output_type)


def tilt_get(
    resource: str,
    watch: bool = False,
    output_type: str = "json",
    port: int | None = None,
):
    args = ["tilt", "get", resource, "--output", output_type]

    if port:
        args.extend(["--port", port])

    if watch:
        args.extend(["--watch"])

    return run(args, output_type)


def tilt_xable(
    enable: bool = True,
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    op = "enable" if enable else "disable"
    args = ["tilt", op]

    if isinstance(resources, str):
        args.append(resources)
    elif isinstance(resources, list):
        args.extend(resources)

    if labels is not None:
        args.append("--labels")
        if isinstance(labels, str):
            args.append(labels)
        elif isinstance(labels, list):
            args.extend(labels)

    if port:
        args.extend(["--port", port])

    return run(args)


def tilt_enable(
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    return tilt_xable(
        enable=True,
        resources=resources,
        labels=labels,
        port=port,
    )


def tilt_disable(
    resources: str | list[str] | None = None,
    labels: str | list[str] | None = None,
    port: int | None = None,
):
    return tilt_xable(
        enable=False,
        resources=resources,
        labels=labels,
        port=port,
    )


def tilt_trigger(resource: str, port: int | None = None):
    args = ["tilt", "trigger", resource]

    if port:
        args.extend(["--port", port])

    return run(args)


def tilt_patch(
    resource: str,
    config: str,
    patch_type: str = "strategic",
    port: int | None = None,
):
    args = ["tilt", "patch", resource, "--type", patch_type, "-p", config]

    if port:
        args.extend(["--port", port])

    return run(args)


@dataclass
class TiltAPIResource:
    name: str
    port: int

    @property
    def resource_type(self):
        raise NotImplementedError

    @property
    def canonical_name(self):
        return f"{self.resource_type}/{self.name}"

    @property
    def properties(self):
        return tilt_get(self.canonical_name, port=self.port)

    def exists(self) -> bool:
        return bool(self.properties)

    def _test_status(self):
        raise NotImplementedError

    @property
    def is_enabled(self) -> bool | None:
        if self.exists() and self._test_status():
            return True
        return False

    def patch(self, config: dict):
        return tilt_patch(self.canonical_name, json.dumps(config), port=self.port)

    def _push_state(self, enabled: bool = True):
        raise NotImplementedError

    def toggle(self):
        self._push_state(not self.is_enabled)

    def enable(self, wait: bool = False):
        if not self.is_enabled:
            print(f"Tilt UISession @ Port {self.port}: Enabling {self.canonical_name}")
            self.toggle()
            if wait:
                self.wait("condition=Ready=true")

    def disable(self, wait: bool = False):
        print(self.port, self.canonical_name)

        if self.is_enabled:
            print(f"Tilt UISession @ Port {self.port}: Disabling {self.canonical_name}")
            self.toggle()
            if wait:
                self.wait("condition=Ready=false")

    def wait(self, wait_for: str):
        tilt_wait(self.canonical_name, wait_for=wait_for, port=self.port)

    async def watch(self):
        async for resource_object in tilt_watch(
            self.canonical_name,
            output="json",
            port=self.port
        ):
            yield resource_object


@dataclass
class TiltUIButton(TiltAPIResource):
    name: str
    patch_enable: dict
    patch_disable: dict
    port: int
    _last_clicked: datetime | None = None

    @property
    def resource_type(self):
        return "uibutton"

    def _test_status(self) -> bool:
        annotations = self.properties["metadata"]["annotations"]
        return annotations.get("btn-enabled", "false") == "true"

    def _push_state(self, enabled: bool = True):
        config = self.patch_enable if enabled else self.patch_disable
        tilt_patch(
            self.canonical_name,
            json.dumps(config),
            patch_type="json",
            port=self.port
        )

    async def watch(self):
        async for resource_object in super().watch():

            if last_clicked := resource_object["status"]["lastClickedAt"]:
                last_clicked = datetime.fromisoformat(last_clicked)

            if not last_clicked or last_clicked == self._last_clicked:
                self._last_clicked = last_clicked
                # The button was not clicked, ignore this event!
                continue

            self._last_clicked = last_clicked

            annotations = resource_object["metadata"]["annotations"]
            enabled = annotations.get("btn-enabled", "false") == "true"
            if enabled:
                yield DISABLE_SIGNAL
            else:
                yield ENABLE_SIGNAL


@dataclass
class TiltUIResource(TiltAPIResource):
    name: str
    port: int
    toggle_args: dict = field(default_factory=dict)

    @property
    def resource_type(self):
        return "uiresource"

    def _test_status(self) -> bool:
        status = self.properties["status"]["disableStatus"]["state"]
        return status == "Enabled"

    def _push_state(self, enable: bool = True):
        tilt_xable(enable=enable, port=self.port, **self.toggle_args)

        trigger_mode = self.properties["status"].get("triggerMode")
        if enable and trigger_mode is not None:
            print(f"Triggering {self.canonical_name}")
            tilt_trigger(self.name, port=self.port)

    async def watch(self):
        async for resource_object in super().watch():
            status = resource_object["status"]["disableStatus"]["state"]

            if status == ENABLED_STATE:
                yield ENABLE_SIGNAL
            else:
                yield DISABLE_SIGNAL
