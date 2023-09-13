from pathlib import Path

EXTENSION_PATH = Path(__file__).parents[1]

EXTENSION_STATE_DISABLED = "Disabled"
EXTENSION_STATE_ENABLED = "Enabled"

K8S_CONFIGMAP_SESSIONS = "configmap/tilt-active-sessions"
K8S_DEPLOYMENT_DATADOG = "deployment/datadog-cluster-agent"

SVG_DISABLED = EXTENSION_PATH.joinpath("assets/datadog-disabled.svg")
SVG_ENABLED = EXTENSION_PATH.joinpath("assets/datadog-enabled.svg")

TILT_UIBUTTON_TOGGLE_DATADOG_AGENT = "uibutton/de-remote:toggle-datadog-agent"
TILT_UIRESOURCE_DATADOG_AGENT = "uiresource/datadog-agent"
TILT_UIRESOURCE_DATADOG_OPERATOR = "uiresource/datadog-operator"
