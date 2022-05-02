"""Ensure IngressClass is ready to be used.

Minikube and Docker Desktop need to install Ingress differently, so this code is
quite a bit more complicated than a single local_resource pinging a deployment.

The end result is a Tilt workload, normalized as "ingress-nginx" which can be
used to prevent race conditions when applying YAML that includes an ingress.
"""

load("ext://helm_remote", "helm_remote")
load("ext://namespace", "namespace_create")
load("./cluster_discovery.star", "DOCKER_DESKTOP", "MINIKUBE")

def setup_ingress(context):
    if context == MINIKUBE:
        k8s_yaml("k8s/ingressclass.yaml")
        k8s_resource(new_name = "ingress-class", objects = ["nginx:ingressclass"], labels = "ingress")
        local_resource(
            "ingress-nginx-controller",
            serve_cmd = ["sleep", "infinity"],
            serve_cmd_bat = "ping -t localhost > NUL",
            readiness_probe = probe(
                failure_threshold = 3,
                initial_delay_secs = 5,
                period_secs = 10,
                timeout_secs = 2,
                exec = exec_action([
                    "kubectl",
                    "-n",
                    "ingress-nginx",
                    "rollout",
                    "status",
                    "deployment",
                    "ingress-nginx-controller",
                ]),
            ),
            labels = "ingress",
        )

    if context == DOCKER_DESKTOP:
        namespace_create("ingress-nginx")
        helm_remote(
            "ingress-nginx",
            repo_url = "https://kubernetes.github.io/ingress-nginx",
            namespace = "ingress-nginx",
        )
        k8s_resource(new_name = "ingress-class", objects = ["nginx:ingressclass"], labels = "ingress")
        k8s_resource(
            new_name = "ingress-nginx",
            objects = [
                "ingress-nginx:namespace",
                "ingress-nginx:serviceaccount",
                "ingress-nginx:role",
                "ingress-nginx:clusterrole",
                "ingress-nginx:rolebinding",
                "ingress-nginx:clusterrolebinding",
            ],
            resource_deps = ["ingress-class"],
            labels = "ingress",
        )
        k8s_resource(
            "ingress-nginx-admission-create",
            objects = [
                "ingress-nginx-admission:serviceaccount",
                "ingress-nginx-admission:role",
                "ingress-nginx-admission:clusterrole",
                "ingress-nginx-admission:rolebinding",
                "ingress-nginx-admission:clusterrolebinding",
                "ingress-nginx-admission:validatingwebhookconfiguration",
            ],
            resource_deps = ["ingress-nginx"],
            labels = "ingress",
        )
        k8s_resource(
            "ingress-nginx-admission-patch",
            resource_deps = [
                "ingress-nginx",
                "ingress-nginx-admission-create",
            ],
            labels = "ingress",
        )
        k8s_resource(
            "ingress-nginx-controller",
            objects = [
                "ingress-nginx-controller:configmap",
            ],
            resource_deps = [
                "de-tls",
                "ingress-nginx",
                "ingress-nginx-admission-create",
                "ingress-nginx-admission-patch",
            ],
            labels = "ingress",
        )
