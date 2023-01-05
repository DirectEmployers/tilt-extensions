# pip_compile_button

Add a button to a resource to allow [pip-tools requirements](https://pip-tools.readthedocs.io/en/latest/) to be compiled.

## Usage

After importing the repo and extension (see [main README](../README.md)), you can invoke the extension using `pip_compile_button` in your Tiltfile.

```python
pip_compile_button(
    # Tilt resource to attach the button to.
    "resource-name",

    # Paths of requirements files to compile.
    requirements=[
        "requirements.in",
        "requirements-dev.in",
    ],

    # Local Destination for compiled requirements.
    destination="./",

    # Optional, use if different than 'deploy/resource-name'.
    exec_path="exec_path",

    # Any arguments you would like to send to pip-compile.
    compile_args=["--quiet", "--cache-dir=DIRECTORY"],
)
```
