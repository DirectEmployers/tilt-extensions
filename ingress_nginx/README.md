# ingress_nginx

Simplify the creation/resource scaffolding of [ingress-nginx](https://kubernetes.github.io/ingress-nginx/) in 
Kubernetes and Tilt, using the official Helm Chart or plugin (in the case of Minikube).

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using 
`ingress_nginx()` in your Tiltfile.

```starlark
load("ext://ingress_nginx", "ingress_nginx")

ingress_nginx(
    # Optional: Useful for ensuring a secret or configmap containing TLS certificates is ready.
    resource_deps = ["de-tls"],
    
    # Optional: Default is "ingress".
    labels = ["backend", "ingress"]
)
```
