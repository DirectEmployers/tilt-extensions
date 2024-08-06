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
```starlark
load("ext://motoserver", "motoserver_up")

motoserver_up()
```

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
