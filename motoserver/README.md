# Moto Server

MotoServer emulates AWS resources for development, using a lightly modified version of the official [Moto Docker image](https://hub.docker.com/r/motoserver/moto).

## Usage

After registering the repo and extension (see [main README](../README.md) for more details), you can invoke the extension using 
`motoserver_up()` in your Tiltfile.

### Register the extension repo
```starlark
v1alpha1.extension_repo(
    name = "de-tilt",
    url = "https://github.com/DirectEmployers/tilt-extensions",
)
```

### Register the `motoserver` extension
```starlark
v1alpha1.extension(
    name = "motoserver",
    repo_name = "de-tilt",
    repo_path = "motoserver",
)
```

### Import and call the extension
Here is the simplest way to get MotoServer running.

```starlark
load("ext://motoserver", "motoserver_up")

motoserver_up()
```

You can also set any labels you may wish MotoServer resources to use:
```starlark
motoserver(labels=["motoserver", "support"])
```

### Provide an initialization script
An init script can be provided via path or string using the `init_script` keyword argument. It will be added to a 
ConfigMap and run during server startup by the Python script in `src/main.py`. Note: your init commands should be
idempotent to prevent duplicate data or errors from occurring (i.e. use checks to prevent existing resources from
being recreated).

> **Important:** The default account ID is `123456789012`. If you have trouble finding resources which ought to exist,
> please try again with an ARN which includes the default region and account ID
> (i.e. arn:aws:sns:us-east-1:123456789012:test_topic).

```starlark
motoserver_up(init_script="path/to/your/init.sh")

# or with a string
motoserver_up(
    init_script="""
    #!/usr/bin/env sh
    echo "=============================================================================================="
    echo "This is a placeholder for a MotoServer init script. See the extension readme for more details!"
    echo "URL: https://github.com/DirectEmployers/tilt-extensions/blob/main/motoserver/README.md"
    echo "=============================================================================================="
    """
)
```

> **Note:** If you encounter trouble with string parsing, you can find more detail about how strings behave in the 
> [Starlark documentation](https://github.com/bazelbuild/starlark/blob/master/spec.md).


#### App Integration using environment variable
After successfully starting, MotoServer should be available within the cluster at `http://motoserver:3000`. 
A limited web dashboard is also available at http://motoserver:3000/moto-api/ 
(after updating your hosts file to include `motoserver`).

The simplest way use MotoServer for all AWS requests in your development environment is by using the `AWS_ENDPOINT_URL`
environment variable in your app containers. [Service-specific endpoints](https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html) can also be used if required for one-off exceptions.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  selector:
    matchLabels:
      app: myapp
  template:
    spec:
      containers:
        - name: myapp
          env:
            - name: AWS_ENDPOINT_URL
              value: "http://motoserver:3000"
```
