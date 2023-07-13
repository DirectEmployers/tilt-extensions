# pip_tools_compiler

Add a "pip-compile" button to a Tilt resource, which will run the [pip-tools](https://pip-tools.readthedocs.io/en/latest/) 
`pip-compile` command to be run in a docker container using the image of your choice.

## Requirements

- Docker (`docker run` is used to run the compile container)
- A Docker image with `pip-tools` pre-installed

## Usage

### Signature

```python
pip_compile_button(resource_name, image, requirements, options = None, install = False)
```

### Parameters

- **resource_name** (`str`) – The name of an existing Tilt resource to add the button to.
- **image** (`str`) – Docker image that will run `pip-compile`.
- **requirements**  (`List[str]`|`str`) – Path(s) to local .in files which pip-tools needs to compile. 
- **options** (`List[str]`|`None`) – Optional options to use with `pip-compile`.
- **install** (`bool`) – Whether to attempt `pip install pip-tools`. Defaults to `False`. 

### Return type

`None`

### Example

After importing the repo and extension (see [main README](../README.md)), you can invoke the extension using `pip_compile_button` in your Tiltfile.

```python
load("ext://pip_tools_compiler", "pip_compile_button")

pip_compile_button(
    "resource-name",
    image = "python:latest",
    requirements = [
        "./requirements.in",
        "./requirements-dev.in",
    ],
    options = [
        "--allow-unsafe",
        "--generate-hashes",
        "--resolver=backtracking",
        "--verbose",
    ],
    install = True,
)
```
