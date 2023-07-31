# tilt-extensions

DirectEmployers Extensions for Tilt

## Importing the repo

```python
v1alpha1.extension_repo(
    name="de-tilt",
    url="https://github.com/DirectEmployers/tilt-extensions",
)
v1alpha1.extension(
    name="pip_compile_button",
    repo_name="de-tilt",
    repo_path="pip_compile_button",
)
```

## Extensions

- [docker_build_remote](./docker_build_remote) - Checkout a remote Dockerfile from Git and build it.
- [pip_compile_button](./pip_compile_button) - Add a pip-compile button to any Tilt resource.
