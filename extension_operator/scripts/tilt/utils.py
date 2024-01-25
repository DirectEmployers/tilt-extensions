from constants import (
    K8S_CONFIGMAP_SESSIONS,
    SESSION_PORT,
    TILT_UIRESOURCE_DATADOG_OPERATOR,
)
from k8s.command import kubectl_get
from tilt.api_resources import TiltUIResource
from tilt.command import tilt_get


def get_or_create_extension_operator():
    for session_port in get_session_ports():
        if tilt_get(TILT_UIRESOURCE_DATADOG_OPERATOR, port=session_port):
            return TiltUIResource("datadog-operator", port=session_port)
    return TiltUIResource("datadog-operator", port=SESSION_PORT)


def get_session_ports():
    cm = kubectl_get(K8S_CONFIGMAP_SESSIONS)
    sessions = cm.get("data", {})
    return list(sessions.keys())
