# docker_build_remote

Checkout a remote Dockerfile from Git and build it.

## Usage

Works almost identically to [`docker_build`](https://docs.tilt.dev/api.html#api.docker_build), with only one change to 
the signature. An `repository_url` argument has been added following the image name, and the path to the build 
context and dockerfile, etc can be passed the same after that.

Builds upon the work of the [`git_resource`](https://github.com/tilt-dev/tilt-extensions/blob/master/git_resource) 
Tilt extention, which manages the `git checkout` behind the scenes (but sadly did not have a method to simply build 
the Docker image without also creating a deployment for it).

After registering the repo and extension (see [main README](../README.md)), you can invoke the extension using 
`docker_build_remote` in your Tiltfile.

```starlark
load("ext://docker_build_remote", "docker_build_remote")

docker_build_remote(
    "postgres-dev",
    "git@github.com:postgis/docker-postgis.git",
    "13-3.3/",
    extra_tag = "postgres-dev:latest",
)
```
