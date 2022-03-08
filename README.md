# tilt-extensions
DirectEmployers Extensions for Tilt

## Importing the repo
```starlark
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
- pip_compile_button - adds button use pip-compile on requirements in a given resource
