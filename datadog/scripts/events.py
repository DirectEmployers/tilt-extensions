from typing import Any, NamedTuple

from variables import TILT_UIBUTTON_TOGGLE_DATADOG_AGENT, TILT_UIRESOURCE_DATADOG_AGENT


class Event(NamedTuple):
    resource: str
    alias: str
    value: Any


class TiltEvents:
    aliases: dict = {
        "datadog:button.click": (
            TILT_UIBUTTON_TOGGLE_DATADOG_AGENT,
            "status.lastClickedAt"
        ),
        "datadog:workload.status": (
            TILT_UIRESOURCE_DATADOG_AGENT,
            "status.disableStatus.state"
        ),
    }

    @classmethod
    def lookup_alias(cls, value: tuple[str, str], default=None):
        for alias, resource_action in cls.aliases.items():
            if value == resource_action:
                return alias
        return default
