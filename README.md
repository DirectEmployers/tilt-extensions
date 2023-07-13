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
    repo_path="pip_tools_compiler",
)
```

## Extensions

- [pip_compile_button](./pip_compile_button) - Deprecated: It is recommended to use `pip_tools_compiler` instead. 
  `pip_compile_button` has many problems (i.e. race conditions, sync loops, and process termination) which are best 
  solved by moving the process outside of the app container using the requirements.
- [pip_tools_compiler](./pip_tools_compiler) - A button for the Tilt UI used to compile pip requirements. Runs in a 
  throwaway container to avoid the problems with `pip_compile_button`.
- [pip_compile_button](./tarfetch) - Reverse filesync alternative which uses `cat` and `tar` to copy files from 
  a container.
