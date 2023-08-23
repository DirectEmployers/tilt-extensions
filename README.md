# tilt-extensions

DirectEmployers Extensions for Tilt

## Extensions

- [docker_build_remote](./docker_build_remote) - Checkout a remote Dockerfile from Git and build it.
- [localstack](./localstack) - Deploy Localstack to emulate AWS resources for development.
- [pip_compile_button](./pip_compile_button) - Add a pip-compile button to any Tilt resource.

## Usage

### Registering Repository and Extensions

The DirectEmployers tilt-extension repo and any desired extensions must be 
imported once per project. If your project has many Tiltfiles, you may wish
to register these in a common Tiltfile.

#### Register Repository

```starlark
# common/Tiltfile

v1alpha1.extension_repo(
    name = "de-tilt",
    url = "https://github.com/DirectEmployers/tilt-extensions",
)

v1alpha1.extension(
    name = "docker_build_remote",
    repo_name = "de-tilt",
    repo_path = "docker_build_remote",
)

v1alpha1.extension(
    name = "localstack",
    repo_name = "de-tilt",
    repo_path = "localstack",
)

v1alpha1.extension(
    name = "pip_compile_button",
    repo_name = "de-tilt",
    repo_path = "pip_compile_button",
)
```

### Importing Extensions

Extensions must be imported in any Tiltfile they are used.

```starlark
# project/Tiltfile

load_dynamic("../common/Tiltfile")
load("ext://localstack", "localstack_up")

localstack_up()
```
