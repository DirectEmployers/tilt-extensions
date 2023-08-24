# Localstack

Installs Localstack to emulate AWS resources for development, deployed 
using the offical [Localstack Helm Chart](https://github.com/localstack/helm-charts/).

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using 
`localstack()` in your Tiltfile.

```starlark
load("ext://localstack", "localstack_up")

localstack_up()
```
