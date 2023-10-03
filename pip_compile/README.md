# pip_compile_button

Add a button to a resource to allow [pip-tools requirements](https://pip-tools.readthedocs.io/en/latest/) to be 
compiled without relying on resources running in Kubernetes. A copy of the 
Docker image is used to compile the requirements using `docker run`.

## Usage

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using `pip_compile_button` in your Tiltfile.

```starlark
load("ext://pip_compile", "pip_compile_button")

pip_compile_button(    
    # Name of the Docker image (same as the first argument of `docker_build`).
    "image-name",
    
    # Optional: Name of build stage to target (same as the `target` argument of `docker_build`).
    target = "build",
    
    # Path to the directory which contains the requirements .in and .txt files.
    reqs_path = "./requirements/",
    
    # Optional arguments to pass to `pip-compile` (Default: `--allow-unsafe --generate-hashes`).
    compile_args = ["--upgrade-package", "black"],
)
```
