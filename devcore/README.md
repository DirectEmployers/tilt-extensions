# Devcore

## What is this?

This extension helps to make Devcore's resources more portable by importing the Devcore Tilt stack when it is needed.
Without this extension, Devcore will not be bootstrapped and its resources (many of which are requirements for our 
projects). Without it, you will likely have issues with Tilt or your applications because they lack a database or 
some other requirement.

## How to Use It

First you'll need to import the DirectEmployers tilt-extensions repo in your project's Tiltfile.

```starlark
v1alpha1.extension_repo(
    name="de-tilt",
    url="https://github.com/DirectEmployers/tilt-extensions",
)
v1alpha1.extension(
    name = "devcore",
    repo_name = "de-tilt",
    repo_path = "devcore",
)
```

Then import the `start_with_devcore` extension.

```starlark
load("ext://pip_compile_button", "pip_compile_button")
```

Lastly, add one line of code to start your project with Devcore. That `__file__` is a required argument needs to be 
provided to the extension _from the calling Tiltfile_. Just copy and paste the below without changing anything, and 
you'll be good!

```starlark
start_with_devcore(__file__)
```

That's it- the whole repo import and setup is ugly and a pain. Sometimes it can be put into another Tiltfile and 
imported, but the `load` statement and `start_with_devcore` calls will need to be in every Tiltfile you plan to use 
`tilt up` with.
