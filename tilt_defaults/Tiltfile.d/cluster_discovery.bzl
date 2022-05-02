"""Discover current OS and supported Kubernetes cluster."""

DOCKER_DESKTOP = "docker-desktop"
MINIKUBE = "minikube"

CURRENT_OS = local(["python3", "-c", "import platform; print(platform.system())"])
DEFAULT_CLUSTER = MINIKUBE if str(CURRENT_OS).strip() == "Linux" else DOCKER_DESKTOP

context = os.environ.get("DEV_CONTEXT", DEFAULT_CLUSTER)
namespace = os.environ.get("DEV_NAMESPACE", "default")

allow_k8s_contexts(context)
local(["kubectl", "config", "use-context", context, "--namespace", namespace])
