"""Allow custom DE Tilt extensions to be loaded and used."""

v1alpha1.extension_repo(
    name = "de-tilt",
    url = "https://github.com/DirectEmployers/tilt-extensions",
)

v1alpha1.extension(
    name = "pip_compile_button",
    repo_name = "de-tilt",
    repo_path = "pip_compile_button",
)
