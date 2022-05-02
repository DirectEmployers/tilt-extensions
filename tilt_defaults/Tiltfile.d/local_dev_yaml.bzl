"""Load and watch a local-dev.yaml file."""

def local_dev(name, path = "k8s/local-dev.yaml", labels = "background"):
    k8s_yaml(path)
    k8s_resource(
        new_name = name,
        objects = ["{}:configmap".format(name)],
        labels = labels,
    )
