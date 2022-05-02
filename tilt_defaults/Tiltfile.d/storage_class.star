"""Ensure the StorageClass is ready to be used.

Stores cluster-specific StorageClass defaults, then performs a simple healthcheck
on it that can be referenced by other Tilt workloads that require a StorageClass.
"""

def setup_storage_class(context):
    sc_name = "standard"
    if context != MINIKUBE:
        sc_name = "hostpath"

    local_resource(
        "hostpath-storage-class",
        serve_cmd = "while :; do sleep 2073600; done",
        serve_cmd_bat = "ping -t localhost > NUL",
        readiness_probe = probe(
            failure_threshold = 3,
            initial_delay_secs = 5,
            period_secs = 10,
            timeout_secs = 2,
            exec = exec_action([
                "kubectl",
                "-n",
                "default",
                "get",
                "storageclass",
                sc_name,
                "-o",
                "jsonpath='{.metadata.annotations.storageclass\\.kubernetes\\.io/is-default-class}'",
            ]),
        ),
        labels = "background",
    )
