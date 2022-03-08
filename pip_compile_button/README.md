# pip_compile_button

Add a button to a resource to allow pip-tools requirements to be compiled.

# Usage
After importing the repo and extension (see main readme), you can invoke the extension using `pip_compile_button` in your Tiltfile.

```skylark
pip_compile_button(
    "resource-name",  # Tilt resource to add button to
    "requirements.in",  # Main requirements file
    "requirements-dev.in",  # Optional, dev requirements file
    "exec_path",  # Optional, use if different than 'deploy/resource-name'
)
```
