# Moto Sync from S3

This extension allows files to be synced from a remote S3 bucket to a mocked instance using [MotoServer](../motoserver/README.md).

This extension makes the following important assumptions:
- A MotoServer instance is already running in our local dev environment
- A bucket with the same name as the one you wish to sync from already exists on the MotoServer
- Appropriate secrets have been provided via .env file

## Usage

After registering the repo and extension (see [main README](../README.md) for more details), you can invoke the extension using
`moto_sync_from_s3()` in your Tiltfile.

### Register the extension repo
```starlark
v1alpha1.extension_repo(
    name = "de-tilt",
    url = "https://github.com/DirectEmployers/tilt-extensions",
)
```

### Register the `moto_sync_from_s3` extension
```starlark
v1alpha1.extension(
    name = "moto_sync_from_s3",
    repo_name = "de-tilt",
    repo_path = "moto_sync_from_s3",
)
```

### Import and call the extension
Here is the simplest way to get MotoServer running.

```starlark
load("ext://moto_sync_from_s3", "moto_sync_from_s3")

moto_sync_from_s3(
    bucket_name = "my_bucket",
    object_prefix = "path/to/sync/",
    dotenv_path = "src/.env",
)
```

This will create a button on the `motoserver` Tilt resource, which do perform the necessary setup and authentication
using the provided secrets. If all goes well, you will be prompted to authenticate with SSO in a web browser.

> **Note:** Talk to the infrastructure team if you don't have SSO setup.

### Options

| Argument        | Description                                         | Examples                                  | Default               |
|-----------------|-----------------------------------------------------|-------------------------------------------|-----------------------|
| bucket_name     | Name of bucket to sync                              | "mybucket"                                | Required              |
| object_prefix   | Optional object prefix/path to select for sync      | "path/to/sync/"                           | `/`                   |
| dotenv_path     | Path to dotenv file                                 | "path/to/.env"<br/>"/path/to/.global.env" | `<project root>/.env` |
| dotenv_prefix   | Optional custom prefix for environment variables    | "S3SYNC_SPECIAL"                          | `S3SYNC`              |
| button_location | Custom button placement (resource name or location) | "motoserver"<br/>"nav"<br/>`location.NAV` | `location.NAV`        |
| sync_on_start   | Whether to sync files on `tilt up`                  | `True`                                    | `False`               |
| resource_deps   | Ignored when `sync_on_start` is `False`.            | `["motoserver", "database"]`              | `["motoserver"]`      |
| labels          | Ignored when `sync_on_start` is `False`.            | `["motoserver"]`                          | `["motoserver"]`      |


### Providing Secrets
Secrets should be provided in the form of a `.env` file. Below are the available options:

```dotenv
S3SYNC_AWS_ACCOUNT_ID=<required>
S3SYNC_AWS_S3_ROLE_NAME=<required>
S3SYNC_AWS_REGION=us-east-1
S3SYNC_AWS_SSO_WEB_START_URL=<required>
S3SYNC_MOTO_SERVER_ENDPOINT=http://motoserver:3000
S3SYNC_MOTO_ACCESS_KEY=A
S3SYNC_MOTO_ACCESS_SECRET_KEY=B
```
> **Note:** If you are using motoserver defaults, then it is likely that only the ones marked `<required>` will be 
> needed. If you need to connect to buckets using different credentials, you can override the default prefix (`S3SYNC`)
> with a value of your own for each special case.
