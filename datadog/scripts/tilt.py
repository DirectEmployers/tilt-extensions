import json
from dataclasses import dataclass, field

from utils import async_run, run
from variables import ENABLED


async def tilt_watch(
    resource: str,
    jsonpath: str,
    watch: bool = True,
    watch_only: bool = False,
    port: int | None = None,
):
    args = [
        "tilt",
        "get",
        resource,
        f'-o=jsonpath={{$.{jsonpath}}}{{"\\n"}}',
    ]

    if watch_only:
        args.append("--watch-only")
    elif watch:
        args.append("--watch")

    if port:
        args.extend(["--port", port])

    async for line in async_run(args):
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
            print(f"UISession @ Port {self.port}: Disabling {self.canonical_name}")
            self.toggle()
            if wait:
                self.wait("condition=Disabled")

    def disable(self, wait: bool = False):
        if self.is_enabled:
            print(f"UISession @ Port {self.port}: Disabling {self.canonical_name}")
            self.toggle()
            if wait:
                self.wait("condition=Ready")

    def wait(self, wait_for: str):
        tilt_wait(self.canonical_name, wait_for=wait_for, port=self.port)


@dataclass
class TiltUIButton(TiltAPIResource):
    name: str
    patch_enable: dict
    patch_disable: dict
    port: int

    @property
    def resource_type(self):
        return "uibutton"

    def _test_status(self) -> bool:
        status = self.properties["spec"]["text"]
        return ENABLED in status

    def _push_state(self, enabled: bool = True):
        config = self.patch_enable if enabled else self.patch_disable
        tilt_patch(
            self.canonical_name,
            json.dumps(config),
            patch_type="json",
            port=self.port
        )


@dataclass
class TiltUIResource(TiltAPIResource):
    name: str
    port: int
    dependencies: list[str] = field(default_factory=list)

    @property
    def resource_type(self):
        return "uiresource"

    def _test_status(self) -> bool:
        status = self.properties["status"]["disableStatus"]["state"]
        return status == "Enabled"

    def _push_state(self, enabled: bool = True):
        resources = self.dependencies + [self.name]
        tilt_xable(enable=enabled, resources=resources, port=self.port)
