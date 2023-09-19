import os
from pathlib import Path

EXTENSION_PATH = Path(__file__).parents[1]

SESSION_PORT = int(os.environ["TILT_PORT"])

ENABLED_STATE = "Enabled"
DISABLED_STATE = "Disabled"

ENABLE_SIGNAL = "Enable"
DISABLE_SIGNAL = "Disable"

K8S_CONFIGMAP_SESSIONS = "configmap/tilt-active-sessions"
K8S_DEPLOYMENT_DATADOG = "deployment/datadog-cluster-agent"

TILT_UIBUTTON_TOGGLE_DATADOG_AGENT = "uibutton/de-remote:toggle-datadog-agent"
TILT_UIRESOURCE_DATADOG_AGENT = "uiresource/datadog-agent"
TILT_UIRESOURCE_DATADOG_OPERATOR = "uiresource/datadog-operator"

SVG_DD_ON = EXTENSION_PATH.joinpath("assets/datadog-enabled.svg")
BUTTON_ENABLED_PATCH = [
    {"op": "replace", "path": "/metadata/annotations/btn-enabled", "value": "true"},
    {"op": "replace", "path": "/spec/text", "value": "Disable Datadog"},
    {"op": "replace", "path": "/spec/iconSVG", "value": SVG_DD_ON.read_text("utf-8")},
]

SVG_DD_OFF = EXTENSION_PATH.joinpath("assets/datadog-disabled.svg")
BUTTON_DISABLED_PATCH = [
    {"op": "replace", "path": "/metadata/annotations/btn-enabled", "value": "false"},
    {"op": "replace", "path": "/spec/text", "value": "Enable Datadog"},
    {"op": "replace", "path": "/spec/iconSVG", "value": SVG_DD_OFF.read_text("utf-8")},
]
