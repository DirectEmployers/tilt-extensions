# pip_compile_button

Add a button to a resource to allow pip-tools requirements to be compiled.

# Usage
After importing the repo and extension (see main readme), you can invoke the extension using `pip_compile_button` in your Tiltfile.

```skylark
pip_compile_button(
    # Tilt resource to add button to
    "resource-name",
    
    # Paths of requirements files to compile
    requirements=[
        "requirements.in",
        "requirements-dev.in",
    ],
    
    # Local Destination for compiled requirements
    destination="./",
    
    # Optional, use if different than 'deploy/resource-name'
    exec_path="exec_path",
)
```
