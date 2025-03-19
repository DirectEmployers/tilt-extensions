# ingress_nginx

Simplify the creation/resource scaffolding of the [NGINX Ingress Controller for Kubernetes](https://kubernetes.github.io/ingress-nginx/) in Tilt, using the official Helm Chart or Minikube plugin.

## Reference

All arguments for `ingress_nginx()` are optional:

- `resource_deps: list[str] = []`

   Specify resources that must exist before the controller may start, such as a secret or a ConfigMap containing TLS certificates. See [Resource Dependencies in the Tilt docs](https://docs.tilt.dev/resource_dependencies.html).

- `labels: str | list[str] = []`

    Add the ingress controller to a group in the Tilt web UI. See [Resource Groups in the Tilt docs](https://docs.tilt.dev/tiltfile_concepts.html#resource-groups). Defaults to `["ingress"]`.

- `helm_chart_version: str | None = None`

    Specify the version of the [ingress-ningx Helm Chart](https://github.com/kubernetes/ingress-nginx/releases?q=helm-chart&expanded=true) to use. Defaults to the latest version. Doesn't do anything when using Minikube.

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using
`ingress_nginx()` in your Tiltfile.

```starlark
load("ext://ingress_nginx", "ingress_nginx")

ingress_nginx(
    resource_deps = ["de-tls"],
    labels = ["backend", "ingress"]
    helm_chart_version = "4.12.0"
)
```
